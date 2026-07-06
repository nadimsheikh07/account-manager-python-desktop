from typing import Optional, Dict, Any, List
from sqlalchemy import func
from config.db import SessionLocal
from src.models.sale import SaleOrder, SaleOrderProduct
from src.models.product import Product


def generate_profit_report(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Generate a simple profit report.

    Uses product.cost as COGS per unit and sale order product price as revenue.
    start_date and end_date are optional ISO date strings (YYYY-MM-DD or full ISO).
    Returns totals and a per-product breakdown.
    """
    with SessionLocal() as db:
        # Totals: revenue and cogs. Start from SaleOrderProduct to avoid ambiguous joins.
        totals_q = (
            db.query(
                func.coalesce(func.sum(SaleOrderProduct.price * SaleOrderProduct.quantity), 0).label("revenue"),
                func.coalesce(func.sum(Product.cost * SaleOrderProduct.quantity), 0).label("cogs"),
            )
            .select_from(SaleOrderProduct)
            .join(Product, SaleOrderProduct.product)
            .join(SaleOrder, SaleOrderProduct.order)
        )

        if start_date:
            totals_q = totals_q.filter(SaleOrder.date >= start_date)
        if end_date:
            totals_q = totals_q.filter(SaleOrder.date <= end_date)

        totals = totals_q.first()
        revenue = float(totals.revenue or 0.0)
        cogs = float(totals.cogs or 0.0)
        gross_profit = revenue - cogs

        # Breakdown by product
        breakdown_q = (
            db.query(
                Product.id,
                Product.name,
                Product.sku,
                func.coalesce(func.sum(SaleOrderProduct.quantity), 0).label("quantity_sold"),
                func.coalesce(func.sum(SaleOrderProduct.price * SaleOrderProduct.quantity), 0).label("revenue"),
                func.coalesce(func.sum(Product.cost * SaleOrderProduct.quantity), 0).label("cogs"),
            )
            .select_from(SaleOrderProduct)
            .join(Product, SaleOrderProduct.product)
            .join(SaleOrder, SaleOrderProduct.order)
        )

        if start_date:
            breakdown_q = breakdown_q.filter(SaleOrder.date >= start_date)
        if end_date:
            breakdown_q = breakdown_q.filter(SaleOrder.date <= end_date)

        breakdown_q = breakdown_q.group_by(Product.id, Product.name, Product.sku)

        breakdown: List[Dict[str, Any]] = []
        for row in breakdown_q:
            rev = float(row.revenue or 0.0)
            c = float(row.cogs or 0.0)
            breakdown.append(
                {
                    "product_id": row.id,
                    "name": row.name,
                    "sku": row.sku,
                    "quantity_sold": int(row.quantity_sold or 0),
                    "revenue": rev,
                    "cogs": c,
                    "profit": rev - c,
                }
            )

        return {
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "breakdown": breakdown,
        }
