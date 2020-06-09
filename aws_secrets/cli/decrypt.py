import click
import yaml
import base64
import boto3
import json
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


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

    if not 'secrets' in data:
        data['secrets'] = []

    if not 'parameters' in data:
        data['parameters'] = []

    _session = session.session()

    for secret in data['secrets']:
        secret['value'] = kms.decrypt(
            _session, secret['value'], kms_arn).decode('utf-8')
            
        try:
            secret['value'] = json.loads(secret['value'])
        except ValueError as e:
            pass

    for parameter in data['parameters']:
        if parameter['type'] == 'SecureString' and type(parameter['value']) is str:
            parameter['value'] = kms.decrypt(
                _session, parameter['value'], kms_arn).decode('utf-8')

    output_file = output if output else f"{env_file}.dec"
    with open(output_file, 'w') as outfile:
        yaml.safe_dump(data, outfile)
