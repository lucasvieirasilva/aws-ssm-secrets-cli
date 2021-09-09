import click
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session


@click.command(name='set-parameter')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', prompt=True, required=True)
@click.option('-d', '--description', help='SSM Parameter Description', required=False)
@click.option('-t', '--type',
              required=True, type=click.Choice(['String', 'SecureString'], case_sensitive=True),
              default='SecureString')
@click.option('-k', '--kms')
@click.option('--profile')
@click.option('--region')
@catch_exceptions
def set_parameter(env_file, name, description, type, kms, profile, region):
    session.aws_profile = profile
    session.aws_region = region
    config = ConfigReader(env_file)
    provider = config.get_provider('parameters')

    context_data = {
        'name': name,
        'type': type,
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

    parameter = provider.find(name)
    if parameter is None:
        parameter = provider.add(context_data)
    else:
        provider.update(context_data)

    config.encrypt()
    config.save()
