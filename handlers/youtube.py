import datetime
import os

import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib import flow
from googleapiclient.http import MediaFileUpload

from handlers import Handler
from video_to_upload import VideoToUpload

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv()


class Youtube(Handler):
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    _SECRETS_FOLDER = "secrets"
    CLIENT_SECRET = os.path.join(_SECRETS_FOLDER, "client_secret.json")
    CLIENT_CREDS = os.path.join(_SECRETS_FOLDER, "token.json")
    SERVICE_ACCOUNT_CREDS = os.path.join(_SECRETS_FOLDER, "service_account.json")
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]

    UPLOADING_MB_PER_SEC = 1.75
    PROCESSING_MB_PER_SEC = 0.66
    EXTRA_TIME_SEC = 300

    ROUND_INTERVAL_MINUTES = 10

    def __init__(self, video: VideoToUpload):
        super().__init__(video)

        self.youtube = None
        self._set_youtube_instance()

    def upload(self) -> dict:
        media_body = MediaFileUpload(self.video.video_file.file_path, chunksize=-1, resumable=True)

        title = self.video.title or ""
        description = self.video.description or ""
        tags = self.video.game.tags or []

        if self.video.video_file.is_short:
            main_tags = [f"#{x}" for x in self.video.game.main_tags]
            main_tags_str = " ".join(main_tags)

            title = f"{self.video.title} {main_tags_str}".strip()
            description = f"{self.video.description}\n#short #shorts".strip()
            tags = ['short', 'shorts'] + tags

        snippet = {
            'title': title,
            'description': description,
            'tags': tags,
            'defaultLanguage': "ru",
            "defaultAudioLanguage": "ru"
        }
        if self.video.game.youtube_category_id:
            snippet['categoryId'] = self.video.game.youtube_category_id

        status = {
            'privacyStatus': 'private',
            "madeForKids": False
        }
        if publish_at := self.video.publish_at:
            status['publishAt'] = publish_at.strftime("%Y-%m-%dT%H:%M:%S%Z")

        body = {
            'snippet': snippet,
            'status': status,
            'recordingDetails': {
                'recordingDate': datetime.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
            }
        }

        request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media_body,
        )

        response = request.execute()
        if self.video.game.youtube_playlist_id:
            self.insert_video_in_playlist(response['id'], self.video.game.youtube_playlist_id)
        return response
        # self.make_video_public(response['id'])

    def insert_video_in_playlist(self, video_id, playlist_id):
        if playlist_id is None:
            return
        body = {
            "kind": "youtube#playlistItem",
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }

        request = self.youtube.playlistItems().insert(
            part="snippet",
            body=body
        )
        request.execute()

    def make_video_public(self, video_id):
        request = self.youtube.videos().list(
            part="status",
            id=video_id
        )
        request.execute()

    # https://stackoverflow.com/questions/73485981/in-python-is-there-any-way-i-can-store-a-resource-object-so-i-can-use-it-late
    def _get_creds(self) -> Credentials:
        creds = None
        if os.path.exists(self.CLIENT_CREDS):
            creds = Credentials.from_authorized_user_file(self.CLIENT_CREDS, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    _flow = flow.InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET, self.SCOPES)
                    creds = _flow.run_local_server(port=0)
            else:
                _flow = flow.InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET, self.SCOPES)
                creds = _flow.run_local_server(port=0)
            with open(self.CLIENT_CREDS, 'w') as token:
                token.write(creds.to_json())
        return creds

    def _set_youtube_instance(self):
        credentials = self._get_creds()
        self.youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        return self.youtube

    def calculate_publish_time(self) -> datetime:
        file_size = self.video.video_file.size
        processing_time = int(file_size / self.UPLOADING_MB_PER_SEC + file_size / self.PROCESSING_MB_PER_SEC)
        full_processing_time = processing_time + self.EXTRA_TIME_SEC

        publish_at = (datetime.datetime.now() + datetime.timedelta(seconds=full_processing_time))
        interval = self.ROUND_INTERVAL_MINUTES * 60
        publish_at = datetime.datetime.fromtimestamp((publish_at.timestamp() // interval + 1) * interval)
        publish_at -= datetime.timedelta(minutes=1)
        return publish_at

    @staticmethod
    def get_studio_link(_id):
        return f"https://studio.youtube.com/video/{_id}/edit"
