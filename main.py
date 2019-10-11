import logging
import sys

from aiohttp import ClientSession, web
from spotify_client import SpotifyClient


routes = web.RouteTableDef()


def is_valid_request(body, slack_channel_id):
    return (
        'event' in body
        and 'links' in body['event']
        and 'channel' in body['event']
        and body['event']['channel'] == slack_channel_id
    )


@routes.post('/')
async def handler(request):
    body = await request.json()
    if 'challenge' in body:
        return web.Response(text=body['challenge'])

    if is_valid_request(body, request.app['spotify_client'].slack_channel_id):
        await request.app['spotify_client'].add_tracks(body['event']['links'])

    return web.Response()


@routes.get('/authorize/')
async def authorize(request):
    if 'code' in request.query:
        await request.app['spotify_client'].authorize(request.query['code'])
        return web.Response(text='Authorized!')

    return web.HTTPFound(request.app['spotify_client'].auth_redirect_url)


async def startup_spotify_client(app):
    app['spotify_client'] = SpotifyClient()
    app['spotify_client'].client_session = await ClientSession().__aenter__()


async def cleanup_spotify_client(spp):
    await app['spotify_client'].client_session.__aexit__(None, None, None)


if __name__ == '__main__':

    if len(sys.argv) != 2 or sys.argv[1] not in ['dev', 'prod']:
        raise ValueError('Expected config param: "dev" or "prod".')

    log_level, port = {
        'dev': (logging.DEBUG, 8080),
        'prod': (logging.INFO, 80),
    }[sys.argv[1]]

    logging.basicConfig(level=log_level)

    app = web.Application()

    app.on_startup.append(startup_spotify_client)
    app.on_cleanup.append(cleanup_spotify_client)
    app.add_routes(routes)

    web.run_app(app, port=port)

