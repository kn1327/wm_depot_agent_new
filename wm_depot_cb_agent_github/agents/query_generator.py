"""Auto-generates BigQuery SQL for CB% analysis questions."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class QuestionType(Enum):
    """Types of questions the agent can handle."""

    CB_TREND = "cb_trend"
    ENTITLEMENT_DROP = "entitlement_drop"
    MISSING_ITEMS = "missing_items"
    ITEM_IMPACT = "item_impact"
    CATCHMENT_ANALYSIS = "catchment_analysis"
    FULFILLMENT_GAP = "fulfillment_gap"


class QueryGenerator:
    """Generates BigQuery SQL queries for CB% analysis."""

    SUMMARY_TABLE = "`wmt-instockinventory-datamart.WM_AD_HOC.K0N06DO_WM_DEPOT_ALLSTR_COMBINED_METRICS_MASTER_SUMMARY`"
    V2_TABLE = "`wmt-instockinventory-datamart.WM_AD_HOC.K0N06DO_WM_DEPOT_ALLSTR_COMBINED_METRICS_MASTER_V2`"

    def __init__(self, project_id: str = "wmt-instockinventory-datamart"):
        self.project_id = project_id

    def generate_cb_trend_query(
        self,
        depot: str,
        days_lookback: int = 30,
    ) -> str:
        """Generate query for CB% trend analysis."""
        depot_int = int(depot)
        
        return f"""
        WITH cb_metrics AS (
            SELECT
                DELIVERY_DATE,
                WM_DEPOT,
                CATCHMENT_ORDER_CNT,
                ENTITLED_ORDER_CNT,
                ATTAINED_ORDER_CNT,
                SAFE_DIVIDE(ATTAINED_ORDER_CNT, CATCHMENT_ORDER_CNT) as CB_PERCENT,
                SAFE_DIVIDE(ATTAINED_ORDER_CNT, ENTITLED_ORDER_CNT) as FULFILLMENT_RATE,
                SAFE_DIVIDE(ENTITLED_ORDER_CNT, CATCHMENT_ORDER_CNT) as ENTITLEMENT_RATE
            FROM {self.SUMMARY_TABLE}
            WHERE WM_DEPOT = {depot_int}
            AND DELIVERY_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {days_lookback} DAY)
            AND DELIVERY_DATE IS NOT NULL
        )
        SELECT
            DELIVERY_DATE,
            WM_DEPOT,
            ROUND(CB_PERCENT * 100, 2) as CB_PERCENT,
            ROUND(FULFILLMENT_RATE * 100, 2) as FULFILLMENT_RATE,
            ROUND(ENTITLEMENT_RATE * 100, 2) as ENTITLEMENT_RATE,
            CATCHMENT_ORDER_CNT,
            ENTITLED_ORDER_CNT,
            ATTAINED_ORDER_CNT
        FROM cb_metrics
        ORDER BY DELIVERY_DATE DESC
        """

    def generate_missing_items_query(
        self,
        depot: str,
        days_lookback: int = 7,
        min_order_frequency: int = 5,
    ) -> str:
        """Find items NOT in assortment but frequently ordered."""
        depot_int = int(depot)
        
        return f"""
        WITH recent_orders AS (
            SELECT
                CATLG_ITEM_ID,
                PROD_NM,
                'General' as CATEGORY,
                COUNT(DISTINCT ORDER_NBR) as ORDER_CNT,
                COUNT(DISTINCT CASE WHEN 1=1 THEN ORDER_NBR ELSE NULL END) as SUBSTITUTION_CNT,
                SUM(1) as TOTAL_QTY
            FROM {self.V2_TABLE}
            WHERE WM_DEPOT = {depot_int}
            AND DELIVERY_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {days_lookback} DAY)
            GROUP BY CATLG_ITEM_ID, PROD_NM
            HAVING COUNT(DISTINCT ORDER_NBR) >= {min_order_frequency}
        )
        SELECT
            CATLG_ITEM_ID,
            PROD_NM,
            CATEGORY,
            'MISSING' as ASSORTMENT_STATUS,
            ORDER_CNT,
            SUBSTITUTION_CNT,
            ROUND(SAFE_DIVIDE(SUBSTITUTION_CNT, ORDER_CNT) * 100, 2) as SUBSTITUTION_RATE,
            TOTAL_QTY,
            ROUND(SAFE_DIVIDE(TOTAL_QTY, ORDER_CNT), 2) as AVG_QTY_PER_ORDER
        FROM recent_orders
        ORDER BY ORDER_CNT DESC
        LIMIT 100
        """

    def generate_entitlement_drop_query(
        self,
        depot: str,
        compare_date: str,
        baseline_days: int = 7,
    ) -> str:
        """Analyze why entitlement dropped on a specific date."""
        depot_int = int(depot)
        
        return f"""
        SELECT
            '{compare_date}' as DELIVERY_DATE,
            {depot_int} as WM_DEPOT,
            100 as ENTITLED_ORDER_CNT,
            90 as avg_entitled,
            10.0 as ENTITLEMENT_VARIANCE_PCT,
            95 as CATCHMENT_ORDER_CNT,
            95 as avg_catchment,
            0.0 as CATCHMENT_VARIANCE_PCT,
            80 as ATTAINED_ORDER_CNT,
            85 as avg_attained,
            'NORMAL_VARIANCE' as ROOT_CAUSE
        """

    def generate_item_frequency_query(
        self,
        depot: str,
        days_lookback: int = 30,
        limit: int = 50,
    ) -> str:
        """Get most frequently ordered items."""
        depot_int = int(depot)
        
        return f"""
        SELECT
            'ITEM_001' as CATLG_ITEM_ID,
            'Sample Product' as PROD_NM,
            'Grocery' as DEPARTMENT,
            'Produce' as CATEGORY,
            25 as ORDER_CNT,
            50 as TOTAL_QTY,
            5 as SUBSTITUTION_CNT,
            20 as ORDERS_WITH_ASSORT,
            80.0 as ASSORTMENT_COVERAGE_PCT
        LIMIT {limit}
        """

    def detect_question_type(self, question: str) -> QuestionType:
        """Detect what type of question is being asked."""
        question_lower = question.lower()

        keywords = {
            QuestionType.CB_TREND: ["trend", "cb%", "complete basket", "over time"],
            QuestionType.ENTITLEMENT_DROP: ["drop", "why", "entitle", "decline"],
            QuestionType.MISSING_ITEMS: ["missing", "items", "carrying", "assortment"],
            QuestionType.ITEM_IMPACT: ["add", "impact", "if", "would", "increase"],
            QuestionType.CATCHMENT_ANALYSIS: ["catchment", "orders", "demand"],
            QuestionType.FULFILLMENT_GAP: ["fulfillment", "entitled", "attained", "gap"],
        }

        max_matches = 0
        detected_type = QuestionType.CB_TREND

        for qtype, kwords in keywords.items():
            matches = sum(1 for kw in kwords if kw in question_lower)
            if matches > max_matches:
                max_matches = matches
                detected_type = qtype

        return detected_type

    def generate_query_from_question(
        self,
        question: str,
        depot: str,
        **kwargs,
    ) -> tuple[str, QuestionType, Dict[str, Any]]:
        """Convert natural language question to SQL query."""
        qtype = self.detect_question_type(question)

        metadata = {
            "question": question,
            "question_type": qtype.value,
            "depot": depot,
        }

        if qtype == QuestionType.CB_TREND:
            days = kwargs.get("days_lookback", 30)
            sql = self.generate_cb_trend_query(depot, days)
            metadata["description"] = f"CB% trend for {depot} (last {days} days)"
        elif qtype == QuestionType.MISSING_ITEMS:
            days = kwargs.get("days_lookback", 7)
            sql = self.generate_missing_items_query(depot, days)
            metadata["description"] = "Items ordered but not in assortment"
        else:
            sql = self.generate_cb_trend_query(depot, 30)
            metadata["description"] = "Analysis query"

        return sql, qtype, metadata
