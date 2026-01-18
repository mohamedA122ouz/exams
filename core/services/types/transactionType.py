from enum import IntEnum


class TransactionType(IntEnum):
    PAYMENT = 0
    REFUND = 1
    @classmethod
    def choices(cls):
        return [(e.value,e.name) for e in cls]