from typing import Optional

import click
from click.core import Context

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session
from aws_secrets.yaml import yaml


@click.command(name='decrypt', help='Decrypt a configuration file')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--output', type=click.Path())
@click.option('--profile', help="AWS Profile", envvar='AWS_PROFILE')
@click.option('--region', help="AWS Region", envvar='AWS_REGION')
@click.pass_context
@catch_exceptions
def decrypt(
    ctx: Context,
    env_file: str,
    output: Optional[str],
    profile: Optional[str],
    region: Optional[str]
):
    """
        Decrypt CLI Commmand `aws-secrets decrypt --help`

        Args:
            ctx (`Context`): click context object
            env_file (`str`): configuration YAML file
            output (`str`, optional): output YAML file path
            profile (`str`, optional): AWS Profile
            region (`str`, optional): AWS Region
    """
    ctx.obj['config_file'] = env_file
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    config.decrypt()

    output_file = output if output else f"{env_file}.dec"
    with open(output_file, 'w') as outfile:
        yaml.dump(config.data, outfile)
