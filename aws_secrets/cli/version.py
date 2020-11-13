import click
from aws_secrets import __version__


@click.command(name='version')
def version():
    click.echo(f"Version: {__version__}")
