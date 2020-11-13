import click
import yaml
import json
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


@click.command(name='encrypt')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--profile')
@click.option('--region')
def encrypt(env_file, profile, region):
    session.aws_profile = profile
    session.aws_region = region
    with open(env_file, 'r') as source:
        data = yaml.safe_load(source.read())

    kms_arn = str(data['kms']['arn'])

    if 'secrets' not in data:
        data['secrets'] = []

    if 'parameters' not in data:
        data['parameters'] = []

    _session = session.session()

    for secret in data['secrets']:
        secret_value = secret['value']

        if type(secret_value) is dict:
            secret_value = json.dumps(secret_value)

        secret['value'] = kms.encrypt(
            _session, secret_value, kms_arn).decode('utf-8')

    for parameter in data['parameters']:
        if parameter['type'] == 'SecureString' and type(parameter['value']) is str:
            parameter['value'] = kms.encrypt(
                _session, parameter['value'], kms_arn).decode('utf-8')

    with open(env_file, 'w') as outfile:
        yaml.safe_dump(data, outfile)
