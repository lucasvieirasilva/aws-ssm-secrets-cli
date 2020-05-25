import yaml
import boto3
import base64
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous.session import session

class ViewParameterResolver():
    def __call__(self, args):
        with open(args.env_file, 'r') as env:
            yaml_data = yaml.safe_load(env.read())

        parameter = next(
            (param for param in yaml_data['parameters'] if param['name'] == args.name), None)

        if parameter is None:
            raise Exception(f'parameter {args.name} not found')

        if parameter['type'] == 'SecureString' and not args.non_decrypt:
            kms_arn = str(yaml_data['kms']['arn'])
            
            param_value = kms.decrypt(
                session(), str(parameter['value']), kms_arn).decode('utf-8')

        else:
            param_value = str(parameter['value'])

        print(param_value)
