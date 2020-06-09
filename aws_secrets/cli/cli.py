import click
import yaml
import os
import sys
from aws_secrets.tags import OutputStackTag, CmdTag
from aws_secrets.miscellaneous import session
from aws_secrets.cli.set_parameter import set_parameter
from aws_secrets.cli.set_secret import set_secret
from aws_secrets.cli.view_parameter import view_parameter
from aws_secrets.cli.view_secret import view_secret
from aws_secrets.cli.deploy import deploy
from aws_secrets.cli.decrypt import decrypt
from aws_secrets.cli.encrypt import encrypt

yaml.SafeLoader.add_constructor('!cf_output', OutputStackTag.from_yaml)
yaml.SafeDumper.add_multi_representer(
    OutputStackTag, OutputStackTag.to_yaml)
yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

@click.group()
def cli():
    pass

cli.add_command(set_parameter)
cli.add_command(set_secret)
cli.add_command(view_parameter)
cli.add_command(view_secret)
cli.add_command(deploy)
cli.add_command(decrypt)
cli.add_command(encrypt)

if __name__ == '__main__':
    cli()