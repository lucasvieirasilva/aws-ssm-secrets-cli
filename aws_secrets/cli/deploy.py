import logging

import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session

logger = logging.getLogger(__name__)


@click.command(name='deploy')
@click.option('-e', '--env-file', help="Environment YAML file", type=click.Path(), required=True)
@click.option('--filter-pattern', help="Filter Pattern", type=str)
@click.option('--dry-run', help="Execution without apply the changes on the environment", is_flag=True)
@click.option('--confirm', help="Confirm prompt before apply the changes", is_flag=True)
@click.option('--only-secrets', help="Deploy only AWS Secrets", is_flag=True)
@click.option('--only-parameters', help="Deploy only SSM Parameters", is_flag=True)
@click.option('--profile', help="AWS Profile")
@click.option('--region', help="AWS Region")
@catch_exceptions
def deploy(env_file, filter_pattern, dry_run, confirm, only_secrets, only_parameters, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)

    if only_secrets is True or (only_secrets is False and only_parameters is False):
        provider = config.get_provider('secrets')
        provider.deploy(filter_pattern, dry_run, confirm)

    if only_parameters is True or (only_secrets is False and only_parameters is False):
        provider = config.get_provider('parameters')
        provider.deploy(filter_pattern, dry_run, confirm)
