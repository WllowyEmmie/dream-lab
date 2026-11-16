"""Errors the store raises. Functions raise these; they don't return None."""


class StoreError(Exception):
    pass


class NotFound(StoreError):
    pass


class BadReference(StoreError):
    pass


class OutOfStock(StoreError):
    pass
