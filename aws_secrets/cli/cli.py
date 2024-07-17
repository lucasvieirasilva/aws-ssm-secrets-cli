import click

from aws_secrets import __name__ as module_name
from aws_secrets.cli.decrypt import decrypt
from aws_secrets.cli.deploy import deploy
from aws_secrets.cli.encrypt import encrypt
from aws_secrets.cli.set_parameter import set_parameter
from aws_secrets.cli.set_secret import set_secret
from aws_secrets.cli.version import version
from aws_secrets.cli.view_parameter import view_parameter
from aws_secrets.cli.view_secret import view_secret
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.helpers.logging import setup_logging


@click.group(help="AWS Secrets CLI")
@click.option(
    "--loglevel",
    help="Log level.",
    required=False,
    default="WARNING",
    show_default=True,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
)
@click.pass_context
@catch_exceptions
def cli(ctx, loglevel: str):
    """
    Root CLI Group `aws-secrets --help`

    Args:
        ctx (`click.Context`): click context object
        loglevel (`str`): log level
    """

    ctx.ensure_object(dict)
    ctx.obj["loglevel"] = loglevel

    setup_logging(module_name, loglevel)


cli.add_command(set_parameter)
cli.add_command(set_secret)
cli.add_command(view_parameter)
cli.add_command(view_secret)
cli.add_command(deploy)
cli.add_command(decrypt)
cli.add_command(encrypt)
cli.add_command(version)
