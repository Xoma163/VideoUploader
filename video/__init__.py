from pathlib import Path

from windows_metadata import WindowsAttributes


class Video:
    def __init__(self, file: str, title: str, description: str = None, tags: list = None):
        self.file: str = file
        self.title: str = title
        self.description: str = description

        attrs = WindowsAttributes(Path(file))
        hours, minutes, seconds = attrs['length'].split(':', 2)

        self.duration = int(seconds) + int(minutes) * 60 + int(hours) * 3600  # sec

        self.tags = tags

    @property
    def is_short(self):
        return self.duration < 60
