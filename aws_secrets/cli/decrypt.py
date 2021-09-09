import click
import yaml
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='decrypt')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--output', type=click.Path())
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def decrypt(env_file, output, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    config.decrypt()

    output_file = output if output else f"{env_file}.dec"
    with open(output_file, 'w') as outfile:
        yaml.safe_dump(config.data, outfile)
