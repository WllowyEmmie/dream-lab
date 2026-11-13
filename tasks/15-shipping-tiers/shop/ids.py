"""SKUs and order IDs are compared after norm(): trimmed and upper-case.

Normalise any ID that comes from outside before using it as a key.
"""


def norm(value: str) -> str:
    return value.strip().upper()
