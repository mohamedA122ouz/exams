from enum import IntEnum


class seenStatus(IntEnum):
    PENDING = 0
    DELIVERED = 1
    RECEIVED = 2
    SEEN = 3
    @classmethod
    def choices(cls):
        return [ (i.value,i.name) for i in cls]
#------------------