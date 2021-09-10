from typing import Optional
import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import CLIError, catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='view-parameter', help='View decrypted SSM parameter value')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def view_parameter(
    env_file: str,
    name: str,
    profile: Optional[str],
    region: Optional[str]
):
    """
        View SSM Parameter value CLI Commmand `aws-secrets view-parameter --help`

        Args:
            env_file (`str`): configuration YAML file
            name (`str`): SSM parameter name
            profile (`str`, optional): AWS Profile
            region (`str`, optional): AWS Region
    """
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    provider = config.get_provider('parameters')
    parameter = provider.find(name)

    if parameter is None:
        raise CLIError(f'parameter {name} not found')

    click.echo(parameter.decrypt())
