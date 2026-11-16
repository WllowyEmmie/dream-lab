"""Dispatch manifests for the warehouse."""
from datetime import date, datetime


def build_manifests(orders) -> dict:
    """orders: a list of (order_ref, placed_at). Returns {dispatch date: sorted order references}."""
    raise NotImplementedError
