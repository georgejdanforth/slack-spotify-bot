import logging

from aiohttp import ClientSession, web
from spotify_client import SpotifyClient


routes = web.RouteTableDef()
spotify_client = SpotifyClient()


def is_valid_request(body):
    return (
        'event' in body
        and 'links' in body['event']
        and 'channel' in body['event']
        and body['event']['channel'] == spotify_client.slack_channel_id
    )


@routes.post('/')
async def handler(request):
    body = await request.json()
    if 'challenge' in body:
        return web.Response(text=body['challenge'])

    import json
    if is_valid_request(body):
        await spotify_client.add_tracks(body['event']['links'])

    return web.Response()


@routes.get('/authorize/')
async def authorize(request):
    if 'code' in request.query:
        await spotify_client.authorize(request.query['code'])
        return web.Response(text='Authorized!')

    return web.HTTPFound(spotify_client.auth_redirect_url)


@routes.get('/token_info')
async def token_info(request):
    return web.json_response({
        'authorization_code': spotify_client.authorization_code,
        'access_token': spotify_client.access_token,
        'token_expires': str(spotify_client.token_expires),
        'refresh_token': spotify_client.refresh_token,
        'scope': spotify_client.scope
    })


if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app)
