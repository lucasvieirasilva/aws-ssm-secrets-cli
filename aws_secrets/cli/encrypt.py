from typing import Optional

import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session
from click.core import Context


@click.command(name='encrypt', help='Encrypt a configuration file')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--profile', help="AWS Profile", envvar='AWS_PROFILE')
@click.option('--region', help="AWS Region", envvar='AWS_REGION')
@click.pass_context
@catch_exceptions
def encrypt(
    ctx: Context,
    env_file: str,
    profile: Optional[str],
    region: Optional[str]
):
    """
        Encrypt CLI Commmand `aws-secrets encrypt --help`

        Args:
            ctx (`Context`): click context object
            env_file (`str`): configuration YAML file
            profile (`str`, optional): AWS Profile
            region (`str`, optional): AWS Region
    """
    ctx.obj['config_file'] = env_file
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    config.encrypt()
    config.save()
