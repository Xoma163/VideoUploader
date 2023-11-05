from datetime import datetime, timedelta

from handlers.youtube import Youtube
from video import Video


def main():
    dt_now = datetime.now()

    publish_dt = dt_now + timedelta(minutes=20)
    # publish_dt = datetime(
    #     year=2023, month=11, day=5,
    #     hour=15, minute=0, second=0
    # )

    video = Video(
        file=r'C:\Users\Xoma163\Downloads\video.mp4',
        title="Тестовое название",
        description="Тестовое описание",
        tags=["тег1", "тег2"],
        publish=publish_dt
    )
    youtube = Youtube()
    youtube.upload(video, category_id=20)


if __name__ == '__main__':
    main()
