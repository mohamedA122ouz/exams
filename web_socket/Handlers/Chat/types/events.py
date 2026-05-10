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
    UserJoined = "Joined"
    SystemWarning = "Warning"
    SystemError = "Error"
    SystemInfo = "Info"
#------------------