import yaml
import base64
import boto3
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous.session import session


class DeployResolver():
    def __call__(self, args):
        with open(args.env_file, 'r') as env:
            yaml_data = yaml.safe_load(env.read())

        _session = session()
        ssm = _session.client('ssm')
        secretsmanager = _session.client('secretsmanager')

        kms_arn = str(yaml_data['kms']['arn'])

        if 'secrets' in yaml_data:
            for secret in yaml_data['secrets']:
                response = secretsmanager.list_secrets()

                aws_secret = next((item for item in response['SecretList'] if item['Name'] == secret['name']), None)

                if aws_secret:
                    print(f"put secret {secret['name']} on aws environment")
                    secretsmanager.put_secret_value(
                        SecretId=aws_secret['ARN'],
                        SecretString=kms.decrypt(_session, secret['value'], kms_arn).decode('utf-8')
                    )
                else:
                    print(f"creating secret {secret['name']} on aws environment")
                    secretsmanager.create_secret(
                        Name=secret['name'],
                        Description=secret['description'] if 'description' in secret else '',
                        SecretString=kms.decrypt(_session, secret['value'], kms_arn).decode('utf-8')
                    )

        if 'parameters' in yaml_data:
            for parameter in yaml_data['parameters']:
                param_value = ''
                try:
                    param_response = ssm.get_parameter(
                        Name=parameter['name'],
                        WithDecryption=True if parameter['type'] == 'SecureString' else False
                    )

                    param_value = param_response['Parameter']['Value']
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ParameterNotFound':
                        pass
                    else:
                        raise e

                yaml_param_value = str(parameter['value'])
                decrypt_on_deploy = parameter['decryptOnDeploy'] if 'decryptOnDeploy' in parameter else True

                if parameter['type'] == 'SecureString' and decrypt_on_deploy:
                    yaml_param_value = kms.decrypt(_session, yaml_param_value, kms_arn).decode('utf-8')

                if param_value == yaml_param_value:
                    print(f"parameter {parameter['name']} has not changed")
                else:
                    print(f"put parameter {parameter['name']} on aws environment")
                    ssm.put_parameter(
                        Name=parameter['name'],
                        Description=parameter['description'] if 'description' in parameter else '',
                        Value=yaml_param_value,
                        Type=parameter['type'],
                        Overwrite=True,
                    )
