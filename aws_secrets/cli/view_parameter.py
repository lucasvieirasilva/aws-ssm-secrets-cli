import click
import yaml
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session


@click.command(name='view-parameter')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', required=True)
@click.option('--non-decrypt', is_flag=True)
@click.option('--profile')
@click.option('--region')
def view_parameter(env_file, name, non_decrypt, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    parameter = next(
        (param for param in yaml_data['parameters'] if param['name'] == name), None)

    if parameter is None:
        raise Exception(f'parameter {name} not found')

    if parameter['type'] == 'SecureString' and not non_decrypt:
        kms_arn = str(yaml_data['kms']['arn'])

        param_value = kms.decrypt(
            session.session(), str(parameter['value']), kms_arn).decode('utf-8')

    else:
        param_value = str(parameter['value'])

    print(param_value)
