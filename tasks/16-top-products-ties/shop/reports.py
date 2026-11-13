from collections import Counter

from . import clock


def daily_sales(orders, day=None) -> int:
    """Net sales in kobo for one UTC day (default: today), placed orders only."""
    day = day or clock.now().date()
    return sum(o.total - o.refunded for o in orders.all()
               if o.status == "placed" and o.created_at.date() == day)


def top_products(orders, n=3) -> list:
    """SKUs by units sold in placed orders, most first; ties in alphabetical order."""
    counts = Counter()
    for o in orders.all():
        if o.status == "placed":
            counts.update(o.lines)
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [sku for sku, _ in ranked[:n]]
