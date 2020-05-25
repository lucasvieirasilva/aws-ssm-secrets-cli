import yaml
import boto3
import base64
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous.session import session


class SetParameterResolver():
    def __call__(self, args):
        if args.env_file is None:
            raise ValueError('-e or --env-file is required to this operation')

        if args.parameter is None:
            raise ValueError('-p or --parameter is required to this operation')

        if args.value is None:
            raise ValueError('-v or --value is required to this operation')

        with open(args.env_file, 'r') as env:
            yaml_data = yaml.safe_load(env.read())

        print(f'Putting parameter {args.parameter} value with {args.value}')

        parameter = next(
            (param for param in yaml_data['parameters'] if param['name'] == args.parameter), None)

        if parameter is None:
            if args.type is None:
                raise ValueError('-t or --type is required to this operation')

            parameter = {
                'name': args.parameter,
                'type': args.type
            }
            yaml_data['parameters'].append(parameter)

        if parameter['type'] == 'SecureString':
            kms_arn = str(yaml_data['kms']['arn'])

            encrypted_value = kms.encrypt(session(), args.value, kms_arn)
            parameter['value'] = encrypted_value.decode('utf-8')

        elif parameter['type'] == 'string':
            parameter['value'] = args.value

        with open(args.env_file, 'w') as outfile:
            yaml.safe_dump(yaml_data, outfile)
