import os
from dataclasses import dataclass

from dotenv import load_dotenv


CONFIG_VARS = [
    'SERVER_DOMAIN',
    'SLACK_CHANNEL_ID',
    'SPOTIFY_CLIENT_ID',
    'SPOTIFY_CLIENT_SECRET',
    'SPOTIFY_PLAYLIST_ID',
]


@dataclass
class Config:
    server_domain: str
    slack_channel_id: str
    spotify_client_id: str
    spotify_client_secret: str
    spotify_playlist_id: str


def load_config(config_path):
    if config_path:
        load_dotenv(dotenv_path=config_path)

    config_dict = {
        config_var.lower(): os.environ[config_var]
        for config_var in CONFIG_VARS
    }

    return Config(**config_dict)
