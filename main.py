from handlers.youtube import Youtube
from video import Video


def main():
    video = Video(
        file=r'path to videofile',
        title="Название",
        description="Описание",
        tags=["тег1", "тег2"]
    )
    youtube = Youtube()
    youtube.upload(video, category_id=20)


if __name__ == '__main__':
    main()
