from video_to_upload import VideoToUpload


class Handler:
    def __init__(self, video: VideoToUpload):
        self.video: VideoToUpload = video

    def upload(self, **kwargs):
        raise NotImplementedError

    def calculate_publish_time(self):
        pass
