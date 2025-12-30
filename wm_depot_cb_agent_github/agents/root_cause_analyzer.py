"""Analyzes root causes of CB% and entitlement drops."""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RootCauseType(Enum):
    """Types of root causes for metric drops."""

    ASSORTMENT_GAP = "assortment_gap"
    CATCHMENT_DROP = "catchment_drop"
    FULFILLMENT_ISSUE = "fulfillment_issue"
    SEASONAL_ITEM_LOSS = "seasonal_item_loss"
    NORMAL_VARIANCE = "normal_variance"


@dataclass
class RootCauseAnalysis:
    """Result of root cause analysis."""

    depot: str
    analysis_date: str
    primary_cause: RootCauseType
    confidence_score: float
    cb_variance_pct: float
    entitlement_variance_pct: float
    catchment_variance_pct: float
    fulfillment_rate_pct: float
    findings: List[str]
    missing_items_list: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "depot": self.depot,
            "analysis_date": self.analysis_date,
            "primary_cause": self.primary_cause.value,
            "confidence_score": round(self.confidence_score, 3),
            "cb_variance_pct": round(self.cb_variance_pct, 2),
            "entitlement_variance_pct": round(self.entitlement_variance_pct, 2),
            "catchment_variance_pct": round(self.catchment_variance_pct, 2),
            "fulfillment_rate_pct": round(self.fulfillment_rate_pct, 2),
            "findings": self.findings,
            "missing_items_list": self.missing_items_list or [],
            "recommendations": self.recommendations or [],
        }


class RootCauseAnalyzer:
    """Analyzes root causes of metric drops."""

    CATCHMENT_DROP_THRESHOLD = -10.0
    ENTITLEMENT_DROP_THRESHOLD = -15.0
    FULFILLMENT_ISSUE_THRESHOLD = 0.75
    NORMAL_VARIANCE_BAND = 10.0

    def analyze_entitlement_drop(
        self,
        current_data: Dict[str, Any],
        baseline_data: Dict[str, Any],
        missing_items: Optional[List[Dict[str, Any]]] = None,
    ) -> RootCauseAnalysis:
        """Analyze why entitlement dropped."""
        depot = current_data.get("depot", "UNKNOWN")
        analysis_date = current_data.get("date", "")

        entitled_current = current_data.get("entitled_count", 0)
        entitled_baseline = baseline_data.get("avg_entitled", 0)
        entitled_variance = self._calculate_variance(entitled_current, entitled_baseline)

        catchment_current = current_data.get("catchment_count", 0)
        catchment_baseline = baseline_data.get("avg_catchment", 0)
        catchment_variance = self._calculate_variance(catchment_current, catchment_baseline)

        attained_current = current_data.get("attained_count", 0)
        attained_baseline = baseline_data.get("avg_attained", 0)
        cb_variance = self._calculate_variance(attained_current, attained_baseline)

        fulfillment_rate = (
            (attained_current / entitled_current) * 100 if entitled_current > 0 else 0
        )

        primary_cause, confidence = self._determine_primary_cause(
            entitled_variance,
            catchment_variance,
            fulfillment_rate,
            missing_items,
        )

        findings = self._generate_findings(
            primary_cause,
            entitled_variance,
            catchment_variance,
            fulfillment_rate,
            missing_items,
        )

        recommendations = self._generate_recommendations(
            primary_cause, missing_items, fulfillment_rate
        )

        return RootCauseAnalysis(
            depot=depot,
            analysis_date=analysis_date,
            primary_cause=primary_cause,
            confidence_score=confidence,
            cb_variance_pct=cb_variance,
            entitlement_variance_pct=entitled_variance,
            catchment_variance_pct=catchment_variance,
            fulfillment_rate_pct=fulfillment_rate,
            findings=findings,
            missing_items_list=missing_items,
            recommendations=recommendations,
        )

    def _determine_primary_cause(
        self,
        entitlement_variance: float,
        catchment_variance: float,
        fulfillment_rate: float,
        missing_items: Optional[List[Dict[str, Any]]],
    ) -> tuple[RootCauseType, float]:
        """Determine the primary root cause."""
        causes = []

        if catchment_variance < self.CATCHMENT_DROP_THRESHOLD:
            causes.append(
                (RootCauseType.CATCHMENT_DROP, 0.8 + abs(catchment_variance) / 100)
            )

        if (
            entitlement_variance < self.ENTITLEMENT_DROP_THRESHOLD
            and catchment_variance > self.CATCHMENT_DROP_THRESHOLD
        ):
            confidence = 0.7 + (abs(entitlement_variance) / 100)
            if missing_items and len(missing_items) > 5:
                confidence = min(0.95, confidence + 0.1)
            causes.append((RootCauseType.ASSORTMENT_GAP, confidence))

        if fulfillment_rate < self.FULFILLMENT_ISSUE_THRESHOLD:
            causes.append(
                (RootCauseType.FULFILLMENT_ISSUE, (1 - fulfillment_rate / 100) * 0.8)
            )

        if not causes and abs(entitlement_variance) <= self.NORMAL_VARIANCE_BAND:
            return RootCauseType.NORMAL_VARIANCE, 0.8

        if causes:
            causes.sort(key=lambda x: x[1], reverse=True)
            return causes[0]

        return RootCauseType.NORMAL_VARIANCE, 0.5

    def _generate_findings(
        self,
        cause: RootCauseType,
        entitlement_variance: float,
        catchment_variance: float,
        fulfillment_rate: float,
        missing_items: Optional[List[Dict[str, Any]]],
    ) -> List[str]:
        """Generate human-readable findings."""
        findings = []

        if cause == RootCauseType.CATCHMENT_DROP:
            findings.append(
                f"🔴 Catchment orders dropped {abs(catchment_variance):.1f}% from baseline."
            )
            findings.append("Possible factors: seasonal demand, competitor activity.")
        elif cause == RootCauseType.ASSORTMENT_GAP:
            findings.append(
                f"🛑 Entitlement dropped {abs(entitlement_variance):.1f}% while catchment remained stable."
            )
            if missing_items:
                findings.append(
                    f"📦 Found {len(missing_items)} items customers are ordering "
                    f"but you're NOT carrying."
                )
        elif cause == RootCauseType.FULFILLMENT_ISSUE:
            findings.append(
                f"⚠️ Fulfillment rate is only {fulfillment_rate:.1f}%."
            )
        else:
            findings.append("✅ Metrics are within normal variance from baseline.")

        return findings

    def _generate_recommendations(
        self,
        cause: RootCauseType,
        missing_items: Optional[List[Dict[str, Any]]],
        fulfillment_rate: float,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if cause == RootCauseType.CATCHMENT_DROP:
            recs.append("🎯 Monitor competitive activity in your catchment.")
            recs.append("💰 Consider promotional campaigns to drive demand.")
        elif cause == RootCauseType.ASSORTMENT_GAP:
            recs.append("➕ Add missing items to assortment.")
            recs.append("📋 Review seasonal assortment planning.")
        elif cause == RootCauseType.FULFILLMENT_ISSUE:
            recs.append("🚚 Audit fulfillment operations and stock levels.")
            recs.append("⏱️ Review delivery window constraints.")

        recs.append("📊 Monitor metrics daily to catch changes early.")
        return recs

    @staticmethod
    def _calculate_variance(current_value: float, baseline_value: float) -> float:
        """Calculate % variance from baseline."""
        if baseline_value == 0:
            return 0.0
        return ((current_value - baseline_value) / baseline_value) * 100
