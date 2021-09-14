import click
from aws_secrets import __version__


@click.command(name='version', help='Print version')
def version():
    """
        Version command `aws-secrets version`
    """
    click.echo(f"Version: {__version__}")
