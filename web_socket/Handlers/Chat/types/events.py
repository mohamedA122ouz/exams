from enum import StrEnum


class Events(StrEnum):
    UserTyping = "Typing"
    UserSending = "Sending"
    UserRecording = "Recording"
    UserDownloading = "Downloading"
    UserSeen = "Seen"
    UserDeleted = "Deleted"
    UserEdited = "Edited"
    UserReacted = "Reacted"
    UserPinned = "Pinned"
    UserUnpinned = "Unpinned"
    UserLeft = "Left"
    UserMessage = "Message"
    UserJoined = "Joined"
    SystemWarning = "Warning"
    SystemError = "Error"
    SystemInfo = "Info"
    @classmethod
    def choices(cls):
        return [(event.value, event.name) for event in cls]
#------------------