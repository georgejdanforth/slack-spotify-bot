from aiohttp import ClientSession, web

from slack_spotify_bot.config import Config
from slack_spotify_bot.spotify_client import SpotifyClient


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


def run_app(port: int, config: Config):

    async def on_startup(app):
        client_session = await ClientSession().__aenter__()
        app['spotify_client'] = SpotifyClient(client_session, config)

    async def on_cleanup(app):
        await app['spotify_client'].client_session.__aexit__(None, None, None)

    app = web.Application()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)

    web.run_app(app, port=port)
