import yaml
import boto3
import base64
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous.session import session


class SetParameterResolver():
    def __call__(self, args):
        with open(args.env_file, 'r') as env:
            yaml_data = yaml.safe_load(env.read())

        print(f'Putting parameter {args.name} value with {args.value}')

        parameter = next(
            (param for param in yaml_data['parameters'] if param['name'] == args.name), None)

        if parameter is None:
            parameter = {
                'name': args.name,
                'type': args.type
            }
            yaml_data['parameters'].append(parameter)

        if parameter['type'] == 'SecureString':
            kms_arn = str(yaml_data['kms']['arn'])

            encrypted_value = kms.encrypt(session(), args.value, kms_arn)
            parameter['value'] = encrypted_value.decode('utf-8')
        else:
            parameter['value'] = args.value

        with open(args.env_file, 'w') as outfile:
            yaml.safe_dump(yaml_data, outfile)
