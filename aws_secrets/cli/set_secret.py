import click
import yaml
import boto3
import base64
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


@click.command(name='set-secret')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('-k', '--kms')
@click.option('--profile')
@click.option('--region')
def set_secret(env_file, name, type, kms, profile, region):
    session.aws_profile = profile
    session.aws_region = region
    
    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    if not 'secrets' in yaml_data:
        yaml_data['secrets'] = []

    secret = next(
        (secret for secret in yaml_data['secrets'] if secret['name'] == name), None)

    if secret is None:
        secret = {
            'name': name
        }
        yaml_data['secrets'].append(secret)

    if kms:
        secret['kms'] = kms

    kms_arn = str(yaml_data['kms']['arn'])

    print("Enter/Paste your secret. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    value = '\n'.join(contents)

    encrypted_value = kms.encrypt(session.session(), value, kms_arn)
    secret['value'] = encrypted_value.decode('utf-8')

    with open(env_file, 'w') as outfile:
        yaml.safe_dump(yaml_data, outfile)
