import json
import os
from datetime import datetime

import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib import flow
from googleapiclient.http import MediaFileUpload
from google.auth.exceptions import RefreshError
from handlers import Handler
from video import Video

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv()


class Youtube(Handler):
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET_FILE_NAME")
    CLIENT_CREDS = "secrets/token.json"
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtubepartner",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]

    PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")

    def __init__(self):
        self.youtube = None
        self._set_youtube_instance()

    def upload(self, video: Video, **kwargs):
        media_body = MediaFileUpload(video.file, chunksize=-1, resumable=True)

        title = video.title or ""
        description = video.description or ""
        tags = video.tags or []

        if video.is_short:
            main_tags = [f"#{x}" for x in video.main_tags]
            main_tags_str = " ".join(main_tags)

            title = f"{video.title} {main_tags_str}".strip()
            description = f"{video.description}\n#short #shorts".strip()
            tags = ['short', 'shorts'] + video.tags

        snippet = {
            'title': title,
            'description': description,
            'tags': tags,
            'defaultLanguage': "ru",
            "defaultAudioLanguage": "ru"
        }
        if category_id := kwargs.get('category_id'):
            snippet['categoryId'] = category_id

        status = {
            'privacyStatus': 'private',
            "madeForKids": False
        }
        if publish_at := video.publish:
            status['publishAt'] = publish_at.strftime("%Y-%m-%dT%H:%M:%SZ")

        body = {
            'snippet': snippet,
            'status': status,
            'recordingDetails': {
                'recordingDate': datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
            }
        }

        request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media_body,
        )

        response = request.execute()
        print(response)
        studio_link = f"https://studio.youtube.com/video/{response['id']}/edit"
        print(f"Edit your video here - {studio_link}")

        self.insert_video_in_playlist(response['id'])
        # self.make_video_public(response['id'])

    def insert_video_in_playlist(self, video_id):
        if self.PLAYLIST_ID is None:
            return
        body = {
            "kind": "youtube#playlistItem",
            "snippet": {
                "playlistId": self.PLAYLIST_ID,
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
        response = request.execute()
        print(response)

    def make_video_public(self, video_id):
        request = self.youtube.videos().list(
            part="status",
            id=video_id
        )
        response = request.execute()
        print(response)

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
