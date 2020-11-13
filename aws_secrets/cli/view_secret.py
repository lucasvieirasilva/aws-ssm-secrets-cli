import click
import yaml
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


@click.command(name='view-secret')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('--profile')
@click.option('--region')
def view_secret(env_file, name, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    secret = next(
        (param for param in yaml_data['secrets'] if param['name'] == name), None)

    if secret is None:
        raise Exception(f'secret {name} not found')

    kms_arn = str(yaml_data['kms']['arn'])

    param_value = kms.decrypt(
        session.session(), str(secret['value']), kms_arn).decode('utf-8')

    print(param_value)
