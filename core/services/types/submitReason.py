from enum import IntEnum


class SubmitReason(IntEnum):
    TIME_ENDED = 0
    SUBMITTED = 1
    KICKED = 2
    CONNECTION_LOST = 3
    CONNECTION_LOST_TIME_ENDED = 4
    BLACKLISTED = 5
    CURRENTLY_ACTIVE = 6
    @classmethod
    def choices(cls):
        return [(e.value,e.name) for e in cls]
#------------------