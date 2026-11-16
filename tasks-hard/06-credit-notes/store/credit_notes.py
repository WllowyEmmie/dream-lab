"""Credit notes issued to customers."""
from .errors import NotFound


class CreditNotes:
    def __init__(self):
        self._notes = {}

    def issue(self, ref: str, amount: int) -> None:
        """Record a credit note. Issuing the same reference twice raises ValueError."""
        raise NotImplementedError

    def get(self, ref: str) -> int:
        """Amount of a credit note. Raises NotFound if there isn't one."""
        raise NotImplementedError

    def refs(self) -> list:
        """All credit note references, sorted."""
        raise NotImplementedError
