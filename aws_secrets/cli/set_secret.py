import logging

import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session

logger = logging.getLogger(__name__)


@click.command(name='set-secret')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('-d', '--description', help='Secret Description', required=False)
@click.option('-k', '--kms')
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def set_secret(env_file, name, description, kms, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    provider = config.get_provider('secrets')

    context_data = {
        'name': name
    }

    if description:
        context_data['description'] = description

    if kms:
        context_data['kms'] = kms

    click.echo("Enter/Paste your secret. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    context_data['value'] = '\n'.join(contents)

    secret = provider.find(name)
    if secret is None:
        secret = provider.add(context_data)
    else:
        provider.update(context_data)

    config.encrypt()
    config.save()
