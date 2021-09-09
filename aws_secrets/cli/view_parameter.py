import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import CLIError, catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='view-parameter')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('--non-decrypt', is_flag=True)
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def view_parameter(env_file, name, non_decrypt, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    provider = config.get_provider('parameters')
    parameter = provider.find(name)

    if parameter is None:
        raise CLIError(f'parameter {name} not found')

    click.echo(parameter.decrypt())
