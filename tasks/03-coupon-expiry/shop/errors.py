"""Shop errors. Functions raise these when something is wrong; they don't return None."""


class ShopError(Exception):
    pass


class NotFound(ShopError):
    pass


class OutOfStock(ShopError):
    pass


class InvalidCoupon(ShopError):
    pass
