class Game:
    def __init__(
            self,
            main_tags: list[str] = None,
            tags: list[str] = None,
            upload_to_youtube: bool = False,
            youtube_playlist_id: str | None = None,
            youtube_category_id: int | None = None,
            upload_to_google_drive: bool = False,
            google_drive_path: str | None = None,
            save_paths: list[str] = None
    ):
        # основные теги (для youtube shorts)
        self.main_tags: list[str] = main_tags if main_tags else []
        # теги
        self.tags: list[str] = tags if tags else []

        # загружать в ютуб
        self.upload_to_youtube: bool = upload_to_youtube
        # id плейлиста ютуба
        self.youtube_playlist_id: str | None = youtube_playlist_id
        # id категории ютуба
        self.youtube_category_id: int | None = youtube_category_id

        # загружать в гугл драйв
        self.upload_to_google_drive: bool = upload_to_google_drive
        # путь загрузки в гугл драйв
        self.google_drive_path: str | None = google_drive_path

        # путь к директориям куда сохранять видео после загрузки
        self.save_paths: list[str] = save_paths if save_paths else []
