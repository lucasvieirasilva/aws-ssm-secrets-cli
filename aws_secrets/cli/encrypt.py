from typing import Optional
import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='encrypt', help='Encrypt a configuration file')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--profile', envvar='AWS_PROFILE')
@click.option('--region', envvar='AWS_REGION')
@catch_exceptions
def encrypt(
    env_file: str,
    profile: Optional[str],
    region: Optional[str]
):
    """
        Encrypt CLI Commmand `aws-secrets encrypt --help`

        Args:
            env_file (`str`): configuration YAML file
            profile (`str`, optional): AWS Profile
            region (`str`, optional): AWS Region
    """
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    config.encrypt()
    config.save()
