from abc import ABC

from vtaskr.libs.notifications.message import AbstractMessage


class AbstractBaseEmailContent(AbstractMessage, ABC):
    from_email: str | None = None
    to: list[str] = []
    subject: str = ""
    text: str = ""
    html: str = ""
    cc: list[str] | None = None
