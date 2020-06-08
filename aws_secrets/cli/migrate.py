import click
import yaml
import base64
import boto3
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


@click.command(name='migrate')
@click.option('-s', '--source', type=click.Path(), required=True)
@click.option('-t', '--target', type=click.Path(), required=True)
@click.option('--source-profile', required=True)
@click.option('--source-region', required=True)
@click.option('--target-profile', required=True)
@click.option('--target-region', required=True)
def migrate(source, target, source_profile, source_region, target_profile, target_region):
    session.aws_profile = source_profile
    session.aws_region = source_region
    source_session = session.session()
    target_session = boto3.session.Session(region_name=target_region, profile_name=target_profile)

    with open(source, 'r') as source:
        source_data = yaml.safe_load(source.read())

    with open(target, 'r') as target:
        target_data = yaml.safe_load(target.read())

    source_kms_arn = str(source_data['kms']['arn'])
    session.aws_profile = target_profile
    session.aws_region = target_region

    target_kms_arn = str(target_data['kms']['arn'])

    if not 'secrets' in target_data:
        target_data['secrets'] = []

    if not 'parameters' in target_data:
        target_data['parameters'] = []

    for secret in source_data['secrets']:
        target_secret = secret.copy()
        decrypted_data = kms.decrypt(source_session, secret['value'], source_kms_arn).decode('utf-8')
        target_secret['value'] = kms.encrypt(target_session, decrypted_data, target_kms_arn).decode('utf-8')
        target_data['secrets'].append(target_secret)
        

    for parameter in source_data['parameters']:
        target_parameter = parameter.copy()

        if parameter['type'] == 'SecureString' and type(parameter['value']) is str:
            decrypted_data = kms.decrypt(source_session, parameter['value'], source_kms_arn).decode('utf-8')
            target_parameter['value'] = kms.encrypt(target_session, decrypted_data, target_kms_arn).decode('utf-8')

        target_data['parameters'].append(target_parameter)

    with open(target, 'w') as outfile:
        yaml.safe_dump(target_data, outfile)