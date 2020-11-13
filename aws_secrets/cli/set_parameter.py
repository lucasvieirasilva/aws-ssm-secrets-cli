import click
import yaml
from aws_secrets.miscellaneous.kms import encrypt
from aws_secrets.miscellaneous import session


@click.command(name='set-parameter')
@click.option('-e', '--env-file', type=click.Path(), required=True)
@click.option('-n', '--name', prompt=True, required=True)
@click.option('-t', '--type',
              required=True, type=click.Choice(['String', 'SecureString'], case_sensitive=True),
              default='SecureString')
@click.option('-k', '--kms')
@click.option('--profile')
@click.option('--region')
def set_parameter(env_file, name, type, kms, profile, region):
    session.aws_profile = profile
    session.aws_region = region
    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    if 'parameters' not in yaml_data:
        yaml_data['parameters'] = []

    parameter = next(
        (param for param in yaml_data['parameters'] if param['name'] == name), None)

    if parameter is None:
        parameter = {
            'name': name,
            'type': type,
        }
        yaml_data['parameters'].append(parameter)

    if kms:
        parameter['kms'] = kms

    print("Enter/Paste your secret. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)

    value = '\n'.join(contents)

    if parameter['type'] == 'SecureString':
        kms_arn = str(yaml_data['kms']['arn'])
        print('Encrypting the value')
        encrypted_value = encrypt(session.session(), value, kms_arn)
        parameter['value'] = encrypted_value.decode('utf-8')
    else:
        print('Put new value to the parameter')
        parameter['value'] = value

    with open(env_file, 'w') as outfile:
        yaml.safe_dump(yaml_data, outfile)
