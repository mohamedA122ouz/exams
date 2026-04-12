from enum import IntEnum


class NotificationStatus(IntEnum):
    PENDING = 0
    ARRIVED = 1
    READED = 2
    DELETED = 3
    @classmethod
    def choices(cls):
        return [ (i.value,i.name)  for i in cls]
    #---------------
#---------------