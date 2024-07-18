import logging
from typing import Optional

import click
from click.core import Context

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session

logger = logging.getLogger(__name__)


@click.command(name="deploy", help="Deploy resource changes")
@click.option(
    "-e", "--env-file", help="Environment YAML file", type=click.Path(), required=True
)
@click.option("--filter-pattern", help="Filter Pattern", type=str)
@click.option(
    "--dry-run",
    help="Execution without apply the changes on the environment",
    is_flag=True,
)
@click.option("--confirm", help="Confirm prompt before apply the changes", is_flag=True)
@click.option("--only-secrets", help="Deploy only AWS Secrets", is_flag=True)
@click.option("--only-parameters", help="Deploy only SSM Parameters", is_flag=True)
@click.option("--show-diff", help="Show the diff of the changes", is_flag=True)
@click.option("--profile", help="AWS Profile", envvar="AWS_PROFILE")
@click.option("--region", help="AWS Region", envvar="AWS_REGION")
@click.pass_context
@catch_exceptions
def deploy(
    ctx: Context,
    env_file: str,
    filter_pattern: Optional[str],
    dry_run: bool,
    confirm: bool,
    only_secrets: bool,
    only_parameters: bool,
    show_diff: bool,
    profile: Optional[str],
    region: Optional[str],
):
    """
    Deploy CLI Commmand `aws-secrets deploy --help`

    Args:
        ctx (`Context`): click context object
        env_file (`str`): configuration YAML file
        filter_pattern (`str`, optional): resource filter pattern
        dry_run (`bool`): Dry run flag
        confirm (`bool`): Flag to confirm the changes before apply
        only_secrets (`bool`): Only deploy secrets
        only_parameters (`bool`): Only deploy parameters
        show_diff (`bool`): Show the diff of the changes
        profile (`str`, optional): AWS Profile
        region (`str`, optional): AWS Region
    """
    ctx.obj["config_file"] = env_file
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)

    if only_secrets is True or (only_secrets is False and only_parameters is False):
        provider = config.get_provider("secrets")
        provider.deploy(filter_pattern, dry_run, confirm, show_diff)

    if only_parameters is True or (only_secrets is False and only_parameters is False):
        provider = config.get_provider("parameters")
        provider.deploy(filter_pattern, dry_run, confirm, show_diff)
