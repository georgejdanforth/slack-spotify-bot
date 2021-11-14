import click

from slack_spotify_bot.config import load_config


@click.command()
@click.argument('env')
@click.option('-c', '--config', 'config', default=None)
def run(env, config):
    if env == 'dev':
        port = 8080
    elif env == 'prod':
        port = 80
    else:
        raise ValueError(f'Expected env to be one of: "dev", "prod". Got: {env}')

    config = load_config(config)
    print(config)


run()
