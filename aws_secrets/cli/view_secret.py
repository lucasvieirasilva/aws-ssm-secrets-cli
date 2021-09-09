import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import CLIError, catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='view-secret')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def view_secret(env_file, name, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    provider = config.get_provider('secrets')
    secret = provider.find(name)

    if secret is None:
        raise CLIError(f'secret {name} not found')

    click.echo(secret.decrypt())
