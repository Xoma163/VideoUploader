import os
from datetime import datetime

from game import Game
from video_file import VideoFile


class VideoToUpload:
    def __init__(
            self,
            video_file: VideoFile,
            game: Game,
            title: str,
            description: str = None,
            publish_at: datetime | None = None
    ):
        self.video_file: VideoFile = video_file
        self.game: Game = game
        # Заголовок
        self.title: str = title
        # Описание
        self.description: str | None = description

        if not os.path.exists(self.video_file.file_path):
            raise FileExistsError(f"Файл {self.video_file.file_path} не найден")

        # Время публикации
        self.publish_at: datetime | None = publish_at
