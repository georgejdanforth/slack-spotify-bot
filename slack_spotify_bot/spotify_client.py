import base64
import datetime
import json
import re
from urllib.parse import quote_plus

from aiohttp import ClientSession

from slack_spotify_bot.config import Config


class SpotifyClient:

    SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_session: ClientSession, config: Config):

        self.client_session = client_session

        self.server_domain = config.server_domain
        self.slack_channel_id = config.slack_channel_id
        self.spotify_client_id = config.spotify_client_id
        self.spotify_client_secret = config.spotify_client_secret
        self.spotify_playlist_id = config.spotify_playlist_id

        self.authorization_code = None
        self.access_token = None
        self.token_expires = None
        self.refresh_token = None
        self.scope = None
        self.token_type = None

    @property
    def redirect_uri(self):
        return f'http://{self.server_domain}/authorize/'

    @property
    def encoded_redirect_uri(self):
        return quote_plus(self.redirect_uri)

    @property
    def auth_redirect_url(self):
        return (
            f'https://accounts.spotify.com/authorize/'
            f'?client_id={self.spotify_client_id}'
            f'&response_type=code'
            f'&redirect_uri={self.encoded_redirect_uri}'
            f'&scope=playlist-modify-public'
        )

    @property
    def _basic_auth_code(self):
        return 'Basic ' + base64.b64encode(
            f'{self.spotify_client_id}:{self.spotify_client_secret}'.encode('utf-8')
        ).decode('utf-8')

    @property
    def _playlist_add_url(self):
        return f'https://api.spotify.com/v1/playlists/{self.spotify_playlist_id}/tracks'

    def _update_tokens(self, now, token_json):
        seconds = int(token_json.pop('expires_in'))
        self.token_expires = now + datetime.timedelta(seconds=seconds)
        for key, value in token_json.items():
            setattr(self, key, value)

    async def _set_tokens(self):
        headers = {
            'Authorization': self._basic_auth_code,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            'grant_type': 'authorization_code',
            'code': self.authorization_code,
            'redirect_uri': self.redirect_uri
        }

        now = datetime.datetime.utcnow()

        async with self.client_session.post(self.SPOTIFY_TOKEN_URL, headers=headers, params=params) as response:
            response_json = await response.json()
            self._update_tokens(now, response_json)

    async def _refresh_access_token(self):
        headers={
            'Authorization': self._basic_auth_code,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        now = datetime.datetime.utcnow()

        async with self.client_session.post(self.SPOTIFY_TOKEN_URL, headers=headers, params=params) as response:
            response_json = await response.json()
            self._update_tokens(now, response_json)

    async def add_tracks(self, links):
        """
        Extract spotify ID for tracks. Webplayer and desktop app compliant
        """
        track_uris = []
        for link in links:
            match = re.search(r'(?<=track/).+?(?=\?|$)', link['url'])
            if match:
                track_uris.append(f'spotify:track:{match.group()}')

        if not track_uris:
            return

        if datetime.datetime.utcnow() >= self.token_expires:
            await self._refresh_access_token()

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {
            'uris': track_uris,
            'position': 0
        }

        async with self.client_session.post(self._playlist_add_url, headers=headers, json=body) as response:
            print(json.dumps(response.__dict__, default=str, indent=2, sort_keys=True))

    async def authorize(self, authorization_code):
        self.authorization_code = authorization_code
        await self._set_tokens()
