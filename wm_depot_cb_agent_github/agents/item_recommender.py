"""Recommends items to add and simulates their impact on CB%."""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ItemImpactSimulation:
    """Result of item impact simulation."""

    item_id: str
    product_name: str
    category: str
    current_cb_percent: float
    projected_cb_percent: float
    cb_lift_percent: float
    estimated_additional_orders: int
    current_order_count: int
    substitution_count: int
    substitution_rate: float
    avg_qty_per_order: float
    confidence_score: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item_id": self.item_id,
            "product_name": self.product_name,
            "category": self.category,
            "current_cb_percent": round(self.current_cb_percent, 2),
            "projected_cb_percent": round(self.projected_cb_percent, 2),
            "cb_lift_percent": round(self.cb_lift_percent, 3),
            "estimated_additional_orders": self.estimated_additional_orders,
            "current_order_count": self.current_order_count,
            "substitution_count": self.substitution_count,
            "substitution_rate": round(self.substitution_rate, 2),
            "avg_qty_per_order": round(self.avg_qty_per_order, 2),
            "confidence_score": round(self.confidence_score, 3),
            "rationale": self.rationale,
        }


class ItemRecommender:
    """Recommends high-impact items to add to assortment."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def recommend_items(
        self,
        missing_items: List[Dict[str, Any]],
        current_cb_percent: float,
        current_catchment_count: int,
        current_entitled_count: int,
        top_n: int = 10,
    ) -> List[ItemImpactSimulation]:
        """Recommend top N items to add based on impact."""
        if not missing_items:
            return []

        simulations = []
        for item in missing_items:
            simulation = self._simulate_item_impact(
                item,
                current_cb_percent,
                current_catchment_count,
                current_entitled_count,
            )
            simulations.append(simulation)

        simulations.sort(key=lambda x: x.cb_lift_percent, reverse=True)
        return simulations[:top_n]

    def _simulate_item_impact(
        self,
        item: Dict[str, Any],
        current_cb_percent: float,
        current_catchment_count: int,
        current_entitled_count: int,
    ) -> ItemImpactSimulation:
        """Simulate the impact of adding a specific item."""
        item_id = item.get("catlg_item_id", "")
        product_name = item.get("product_name", "Unknown")
        category = item.get("category", "Uncategorized")

        order_count = item.get("order_count", 0)
        substitution_count = item.get("substitution_count", 0)
        substitution_rate = item.get("substitution_rate", 0.0)
        avg_qty_per_order = item.get("avg_qty_per_order", 1.0)

        capture_rate = 0.70
        estimated_additional_orders = int(substitution_count * capture_rate)

        current_attained = self._derive_attained_from_cb(
            current_cb_percent, current_catchment_count
        )

        new_attained = current_attained + estimated_additional_orders
        new_cb_percent = (
            (new_attained / current_catchment_count) * 100
            if current_catchment_count > 0
            else 0
        )

        cb_lift = new_cb_percent - current_cb_percent

        confidence = self._calculate_confidence_score(
            order_count, substitution_rate, estimated_additional_orders
        )

        rationale = self._generate_rationale(
            product_name, order_count, estimated_additional_orders, cb_lift
        )

        return ItemImpactSimulation(
            item_id=item_id,
            product_name=product_name,
            category=category,
            current_cb_percent=current_cb_percent,
            projected_cb_percent=new_cb_percent,
            cb_lift_percent=cb_lift,
            estimated_additional_orders=estimated_additional_orders,
            current_order_count=order_count,
            substitution_count=substitution_count,
            substitution_rate=substitution_rate,
            avg_qty_per_order=avg_qty_per_order,
            confidence_score=confidence,
            rationale=rationale,
        )

    @staticmethod
    def _derive_attained_from_cb(
        cb_percent: float, catchment_count: int
    ) -> int:
        """Derive current attained count from CB% and catchment."""
        if catchment_count == 0:
            return 0
        return int((cb_percent / 100.0) * catchment_count)

    @staticmethod
    def _calculate_confidence_score(
        order_count: int,
        substitution_rate: float,
        estimated_additional_orders: int,
    ) -> float:
        """Calculate confidence in the recommendation."""
        confidence = 0.5

        if order_count >= 50:
            confidence += 0.25
        elif order_count >= 20:
            confidence += 0.15
        elif order_count >= 10:
            confidence += 0.05

        if substitution_rate >= 0.5:
            confidence += 0.2
        elif substitution_rate >= 0.3:
            confidence += 0.1

        if estimated_additional_orders >= 50:
            confidence += 0.1
        elif estimated_additional_orders >= 20:
            confidence += 0.05

        return min(0.95, confidence)

    @staticmethod
    def _generate_rationale(
        product_name: str,
        order_count: int,
        estimated_additional_orders: int,
        cb_lift: float,
    ) -> str:
        """Generate human-readable rationale for recommendation."""
        if cb_lift >= 2.0:
            impact_level = "💥 HIGH IMPACT"
        elif cb_lift >= 1.0:
            impact_level = "🚀 MEDIUM IMPACT"
        else:
            impact_level = "💭 LOW IMPACT"

        return (
            f"{impact_level} - {product_name} has been ordered {order_count} times. "
            f"Adding it would capture ~{estimated_additional_orders} more orders "
            f"and lift CB% by {cb_lift:.2f}pp."
        )

    @staticmethod
    def recommend_category_focus(
        missing_items: List[Dict[str, Any]],
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Identify categories with most missing items."""
        category_stats = {}

        for item in missing_items:
            category = item.get("category", "Uncategorized")
            order_count = item.get("order_count", 0)

            if category not in category_stats:
                category_stats[category] = {
                    "category": category,
                    "item_count": 0,
                    "total_orders": 0,
                }

            category_stats[category]["item_count"] += 1
            category_stats[category]["total_orders"] += order_count

        sorted_cats = sorted(
            category_stats.values(),
            key=lambda x: x["total_orders"],
            reverse=True,
        )

        return sorted_cats[:top_n]
