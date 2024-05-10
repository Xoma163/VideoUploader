import datetime
import shutil

from game import Game
from handlers.youtube import Youtube
from video_file import VideoFile
from video_to_upload import VideoToUpload

DT_STR_FORMAT = '%d.%m.%Y %H:%M'
TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
TIMEZONE_OFFSET = TIMEZONE.utcoffset(datetime.datetime.now()).seconds


def publish_youtube(video: VideoToUpload):
    print("Публикование в ютуб")
    youtube = Youtube(video)
    publish_at: datetime = youtube.calculate_publish_time()
    publish_at_str = publish_at.strftime(DT_STR_FORMAT)
    print(f"Видео будет опубликовано в {publish_at_str}")
    # Ютуб принимает UTC время и ставит таймзону в зависимости от пользователя. Поэтому здесь мы откручиваем наше время
    publish_at -= datetime.timedelta(seconds=TIMEZONE_OFFSET)
    video.publish_at = publish_at
    print("Начал выгружать видео")
    response = youtube.upload()
    print("Закончил выгружать видео")
    studio_link = youtube.get_studio_link(response['id'])
    print(f"Редактируйте видео здесь: {studio_link}")


def publish_google_drive(video: VideoToUpload):
    print("Публикование в гугл драйв")
    print("Начал выгружать видео")
    shutil.copy(video.video_file.file_path, video.game.google_drive_path)
    print("Закончил выгружать видео")


def publish_video(title: str, game: Game, video_file: VideoFile, description: str | None = None):
    video = VideoToUpload(
        video_file=video_file,
        game=game,
        title=title,
        description=description
    )

    print(f"Файл: {video.video_file.file_path}")
    if video.game.upload_to_youtube:
        publish_youtube(video)
    elif video.game.upload_to_google_drive:
        publish_google_drive(video)
    elif video.game.upload_to_google_drive:
        publish_google_drive(video)
    video.video_file.save_to_storage()


def main():
    title = "test title"
    description = None
    game = Game()
    path_to_find_videos = r"path_to_find_video_files"

    video_file = VideoFile(path_to_find_videos, game.save_paths)
    video_file.find()
    publish_video(title, game, video_file, description)


if __name__ == '__main__':
    main()
