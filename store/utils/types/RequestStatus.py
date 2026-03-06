from enum import IntEnum

class RequestStatus(IntEnum):
    ORDER_PLACED = 0
    PROCESSING = 1
    SHIPPED = 2
    DELIVERED = 3
    @classmethod
    def choices(cls):
        return [(e.value,e.name) for e in cls]
#---------------