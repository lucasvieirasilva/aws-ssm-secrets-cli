import click
import yaml
import json
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session
from aws_secrets.representers.literal import Literal


@click.command(name='decrypt')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('--output', type=click.Path())
@click.option('--profile')
@click.option('--region')
def decrypt(env_file, output, profile, region):
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
        secret['value'] = kms.decrypt(
            _session, secret['value'], kms_arn).decode('utf-8')

        try:
            secret['value'] = json.loads(secret['value'])
        except ValueError:
            pass

    for parameter in data['parameters']:
        if parameter['type'] == 'SecureString' and type(parameter['value']) is str:
            decrypted_value = kms.decrypt(
                _session, parameter['value'], kms_arn).decode('utf-8')

            if '\n' in decrypted_value:
                parameter['value'] = Literal(decrypted_value)
            else:
                parameter['value'] = decrypted_value

    output_file = output if output else f"{env_file}.dec"
    with open(output_file, 'w') as outfile:
        yaml.safe_dump(data, outfile)
