import os
import shutil
from pathlib import Path

from windows_metadata import WindowsAttributes


class VideoFile:
    MP4 = ".mp4"

    def __init__(
            self,
            path_to_find: str,
            save_paths: list[str] | None
    ):
        # Где искать видеофайлы
        self.path_to_find: str = path_to_find
        # Путь куда сохранять файл после загрузки
        self.save_paths: list[str] | None = save_paths

        # Название файла
        self.filename: str | None = None
        # Путь файла
        self.file_path: str | None = None
        # Размер файла
        self.size: float | None = None

        # Продолжительность в секундах
        self.duration: int | None = None

    @property
    def is_short(self) -> bool:
        if not self.duration:
            return False
        return self.duration < 60

    def find(self):
        files = [file for file in os.listdir(self.path_to_find) if file.endswith(self.MP4)]
        self.filename = files[0]
        self.file_path = os.path.join(self.path_to_find, self.filename)
        self.size = os.path.getsize(self.file_path) / 1024 / 1024

        try:
            attrs = WindowsAttributes(Path(self.file_path))
            hours, minutes, seconds = attrs['length'].split(':', 2)
            self.duration = int(seconds) + int(minutes) * 60 + int(hours) * 3600  # sec
        except:
            self.duration = None

    def save_to_storage(self):
        if not self.save_paths:
            raise RuntimeError("save_paths is not set.")
        for save_path in self.save_paths:
            new_filename = os.path.join(save_path, self.filename)
            shutil.copy(self.file_path, new_filename)
            print(f"Скопировал файл в {new_filename}")
        os.remove(self.file_path)
        print(f"Удалил файл {self.file_path}")
