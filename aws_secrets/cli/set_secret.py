import logging
from typing import Optional

import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session
from click.core import Context

logger = logging.getLogger(__name__)


@click.command(name='set-secret', help='Add/Update AWS Secrets Manager secrets')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('-d', '--description', help='Secret Description', required=False)
@click.option('-k', '--kms')
@click.option('--profile', help="AWS Profile", envvar='AWS_PROFILE')
@click.option('--region', help="AWS Region", envvar='AWS_REGION')
@click.pass_context
@catch_exceptions
def set_secret(
    ctx: Context,
    env_file: str,
    name: str,
    description: Optional[str],
    kms: Optional[str],
    profile: Optional[str],
    region: Optional[str]
):
    """
        Add/Update AWS Secrets Manager secrets CLI Commmand `aws-secrets set-secret --help`

        Args:
            ctx (`Context`): click context object
            env_file (`str`): configuration YAML file
            name (`str`): SSM parameter name
            description (`str`, optional): SSM parameter description
            kms (`str`, optional): SSM parameter KMS Arn or Id
            profile (`str`, optional): AWS Profile
            region (`str`, optional): AWS Region
    """
    ctx.obj['config_file'] = env_file
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
