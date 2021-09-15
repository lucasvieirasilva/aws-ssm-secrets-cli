"""
Version command (aws-secrets version)
"""

import click
import pkg_resources
from aws_secrets import __title__


@click.command(name='version', help='Print CLI version')
def version():
    """
        Version command prints the CLI version on the console.
    """
    version = pkg_resources.get_distribution(__title__).version
    click.echo(f"Version: {version}")
