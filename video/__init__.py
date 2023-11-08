from datetime import datetime
from pathlib import Path

from windows_metadata import WindowsAttributes


class Video:
    def __init__(self, file: str, title: str, description: str = None, tags: list = None, main_tags=None, publish: datetime = None):
        self.file: str = file
        self.title: str = title
        self.description: str = description

        attrs = WindowsAttributes(Path(file))
        hours, minutes, seconds = attrs['length'].split(':', 2)

        self.duration: int = int(seconds) + int(minutes) * 60 + int(hours) * 3600  # sec

        self.tags: list = tags
        self.main_tags: list = main_tags or []
        self.publish: datetime = publish

    @property
    def is_short(self) -> bool:
        return self.duration < 60
