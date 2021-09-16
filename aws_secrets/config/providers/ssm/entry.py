from typing import Any, Dict, List, Optional

from botocore.session import Session

from aws_secrets.config.providers import BaseEntry
from aws_secrets.miscellaneous import kms


class SSMParameterEntry(BaseEntry):
    def __init__(
        self,
        session: Session,
        kms_arn: str,
        data: Dict[str, Any],
        cipher_text: str = None
    ) -> None:
        super(SSMParameterEntry, self).__init__(session, kms_arn, data, cipher_text)

        self.type = data['type']
        self.client = self.session.client('ssm')

    def schema(self) -> dict:
        return {
            "type": "object",
            "description": "SSM Parameter Entry",
            "required": ["name", "type"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "SSM Parameter Name"
                },
                "type": {
                    "type": "string",
                    "description": "SSM Parameter Type",
                    "enum": ["String", "SecureString"]
                },
                "description": {
                    "type": "string",
                    "description": "SSM Parameter Description"
                }
            }
        }

    def encrypt(self) -> Optional[str]:
        if self.type == 'SecureString' and self.raw_value and isinstance(self.raw_value, str):
            self.logger.warning(f'Parameter - {self.name} - Encrypting...')
            self.cipher_text = kms.encrypt(self.session, self.raw_value, self.kms_arn).decode('utf-8')
            self.logger.debug(f'Parameter - {self.name} - Encrypted')
            return self.cipher_text
        elif self.type == 'SecureString':
            self.logger.debug(f'Parameter - {self.name} Entry already encrypted')
            return self.cipher_text

        return None

    def decrypt(self) -> str:
        def _do_decrypt(value):
            self.logger.debug(f'Parameter - {self.name} - Decrypting entry')
            return kms.decrypt(self.session, value, self.kms_arn).decode('utf-8')

        if self.type == 'SecureString' and self.cipher_text:
            return _do_decrypt(self.cipher_text)
        elif self.type == 'SecureString' and self.cipher_text is None \
                and self.raw_value is not None and isinstance(self.raw_value, str):
            return _do_decrypt(self.raw_value)

        return self.raw_value

    def create(self) -> None:
        args = {
            'Name': self.name,
            'Description': self.description,
            'Type': self.type,
            'Value': str(self.decrypt()),
            'Tags': self.parse_tags()
        }

        if self.kms:
            args['KeyId'] = self.kms

        self.logger.debug(f'Parameter - {self.name} - Create Parameter in the AWS account')
        self.client.put_parameter(**args)
        self.logger.debug(f'Parameter - {self.name} - AWS Resource Created')

    def update(self, changes: Dict[str, Any]) -> None:
        args = {
            'Name': self.name,
            'Description': self.description,
            'Type': self.type,
            'Value': str(self.decrypt()),
            'Overwrite': True
        }

        if self.kms:
            args['KeyId'] = self.kms

        self.logger.debug(f'Parameter - {self.name} - Updating Parameter in the AWS account')
        self.client.put_parameter(**args)
        self.logger.debug(f'Parameter - {self.name} - AWS Resource Updated')

        tags_change = next((c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)
        aws_tags = tags_change['OldValue'] if tags_change is not None else []

        self.remove_tags(aws_tags)

        tags = self.parse_tags()
        if len(tags) > 0:
            self.apply_tags()

    def apply_tags(self) -> None:
        tags = self.parse_tags()
        self.logger.debug(f'Parameter - {self.name} - Applying tags "{tags}" to the AWS resource')
        self.client.add_tags_to_resource(
            ResourceType='Parameter',
            ResourceId=self.name,
            Tags=tags
        )
        self.logger.debug(f'Parameter - {self.name} - tags "{tags}" applied')

    def remove_tags(self, tags: List[Dict[str, str]]) -> None:
        tags_key = list(map(lambda tag: tag['Key'], tags))
        self.logger.debug(f'Parameter - {self.name} - Removing tags "{tags}" from the AWS Resource')
        self.client.remove_tags_from_resource(
            ResourceType='Parameter',
            ResourceId=self.name,
            TagKeys=tags_key
        )
        self.logger.debug(f'Parameter - {self.name} - tags "{tags}" removed')

    def delete(self) -> None:
        self.logger.debug(f'Parameter - {self.name} - Deleting Parameter from AWS account')
        self.client.delete_parameter(
            Name=self.name
        )
        self.logger.debug(f'Parameter - {self.name} - AWS Resource Deleted')

    def changes(self) -> Dict[str, Any]:
        changes = {
            'Exists': False,
            'ChangesList': []
        }

        self.logger.debug(f'Parameter - {self.name} - Listing SSM Parameters based on name')
        aws_parameters = self.client.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Option': 'Equals',
                    'Values': [self.name]
                }
            ]
        )['Parameters']

        if len(aws_parameters) > 0:
            changes['Exists'] = True
            aws_param = aws_parameters[0]

            aws_param_value = self._get_aws_value(aws_param['Type'])
            yaml_param_value = str(self.decrypt())

            if aws_param_value != yaml_param_value:
                changes['ChangesList'].append(
                    {
                        'Key': 'Value',
                        'HasChanges': True,
                        'Replaceable': True,
                        'Value': yaml_param_value,
                        'OldValue': aws_param_value
                    }
                )

            yaml_secret_description = self.description
            aws_secret_description = aws_param.get('Description', '')

            if aws_secret_description != yaml_secret_description:
                changes['ChangesList'].append(
                    {
                        'Key': 'Description',
                        'HasChanges': True,
                        'Replaceable': True,
                        'Value': yaml_secret_description,
                        'OldValue': aws_secret_description
                    }
                )

            if self.kms is not None and self.kms != aws_param['KeyId']:
                changes['ChangesList'].append(
                    {
                        'Key': 'KeyId',
                        'HasChanges': True,
                        'Replaceable': True,
                        'Value': self.kms,
                        'OldValue': aws_param['KeyId']
                    }
                )

            if self.type != aws_param['Type']:
                changes['ChangesList'].append(
                    {
                        'Key': 'Type',
                        'HasChanges': True,
                        'Replaceable': False,
                        'Value': self.type,
                        'OldValue': aws_param['Type']
                    }
                )

            self.logger.debug(f'Parameter - {self.name} - Listing Tags for the AWS resource')
            aws_tags = self.client.list_tags_for_resource(
                ResourceType='Parameter',
                ResourceId=self.name
            )

            yaml_tags_sorted = sorted(self.parse_tags(), key=lambda k: k['Key'])
            aws_tags_sorted = sorted(aws_tags['TagList'], key=lambda k: k['Key'])
            pairs = zip(yaml_tags_sorted, aws_tags_sorted)
            tags_changes = any(x != y for x, y in pairs) or len(yaml_tags_sorted) != len(aws_tags_sorted)

            if tags_changes:
                changes['ChangesList'].append(
                    {
                        'Key': 'Tags',
                        'HasChanges': tags_changes,
                        'Replaceable': True,
                        'Value': yaml_tags_sorted,
                        'OldValue': aws_tags_sorted
                    }
                )

        return changes

    def _get_aws_value(self, type: str) -> str:
        param_response = self.client.get_parameter(
            Name=self.name,
            WithDecryption=True if type == 'SecureString' else False
        )

        return param_response['Parameter']['Value']
