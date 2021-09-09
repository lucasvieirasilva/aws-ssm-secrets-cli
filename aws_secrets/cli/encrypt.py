import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='encrypt')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def encrypt(env_file, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    config.encrypt()
    config.save()
