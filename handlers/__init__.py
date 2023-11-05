from video import Video


class Handler:
    def upload(self, video: Video, **kwargs):
        raise NotImplementedError
