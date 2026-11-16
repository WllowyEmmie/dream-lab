"""Reference numbers for orders, invoices and credit notes."""
from .errors import BadReference


def canonical(ref: str) -> str:
    """Return the stored form of a reference a person typed."""
    return ref
