import json

from botocore.exceptions import ClientError

from aws_secrets.config.providers import BaseEntry
from aws_secrets.miscellaneous import kms


class SecretManagerEntry(BaseEntry):
    def __init__(self, session, kms_arn, data, cipher_text=None) -> None:
        super(SecretManagerEntry, self).__init__(session, kms_arn, data, cipher_text)

        self.client = self.session.client('secretsmanager')

    def encrypt(self):
        if isinstance(self.raw_value, str) or isinstance(self.raw_value, dict):
            if type(self.raw_value) is dict:
                self.raw_value = json.dumps(self.raw_value)

            self.logger.warning(f'Secret - {self.name} - Encrypting...')
            self.cipher_text = kms.encrypt(self.session, self.raw_value, self.kms_arn).decode('utf-8')
            self.logger.debug(f'Secret - {self.name} - Encrypted')
            return self.cipher_text

        self.logger.debug(f'Secret - {self.name} - Entry already encrypted')
        return self.cipher_text

    def decrypt(self):
        def _do_decrypt(value):
            self.logger.debug(f'Secret - {self.name} - Decrypting entry')
            decrypted_value = kms.decrypt(self.session, value, self.kms_arn).decode('utf-8')
            self.plain_text = decrypted_value

        if self.cipher_text:
            _do_decrypt(self.cipher_text)
        elif self.cipher_text is None and self.raw_value is not None and isinstance(self.raw_value, str):
            _do_decrypt(self.raw_value)

        return self.plain_text

    def create(self):
        args = {
            'Name': self.name,
            'Description': self.description,
            'SecretString': self.decrypt(),
            'Tags': self.parse_tags()
        }

        if self.kms:
            args['KmsKeyId'] = self.kms

        self.logger.debug(f'Secret - {self.name} - Create Secret in the AWS account')
        self.client.create_secret(**args)
        self.logger.debug(f'Secret - {self.name} - AWS Resource Created')

    def update(self, changes):
        args = {
            'SecretId': self.name,
            'Description': self.description,
            'SecretString': self.plain_text
        }

        if self.kms:
            args['KmsKeyId'] = self.kms

        self.logger.debug(f'Secret - {self.name} - Updating Secret in the AWS account')
        self.client.update_secret(**args)
        self.logger.debug(f'Secret - {self.name} - AWS Resource Updated')

        tags_change = next((c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)
        aws_tags = tags_change['OldValue'] if tags_change is not None else []

        self.remove_tags(aws_tags)

        tags = self.parse_tags()
        if len(tags) > 0:
            self.apply_tags()

    def apply_tags(self):
        tags = self.parse_tags()
        self.logger.debug(f'Secret - {self.name} - Applying tags "{tags}" to the AWS resource')
        self.client.tag_resource(
            SecretId=self.name,
            Tags=self.parse_tags()
        )
        self.logger.debug(f'Secret - {self.name} - tags "{tags}" applied')

    def remove_tags(self, tags):
        tags_key = list(map(lambda tag: tag['Key'], tags))
        self.logger.debug(f'Secret - {self.name} - Removing tags "{tags}" from the AWS Resource')
        self.client.untag_resource(
            SecretId=self.name,
            TagKeys=tags_key
        )
        self.logger.debug(f'Secret - {self.name} - tags "{tags}" removed')

    def delete(self):
        self.logger.debug(f'Secret - {self.name} - Deleting Secret from AWS account')
        self.client.delete_secret(
            SecretId=self.name,
            ForceDeleteWithoutRecovery=True
        )
        self.logger.debug(f'Secret - {self.name} - AWS Resource Deleted')

    def changes(self):
        changes = {
            'Exists': False,
            'ChangesList': []
        }
        self.logger.debug(f'Secret - {self.name} - Listing AWS Secrets based on the secret name')
        resp = self.client.list_secrets(
            Filters=[
                {
                    'Key': 'name',
                    'Values': [self.name]
                }
            ]
        )

        if len(resp['SecretList']) > 0:
            changes['Exists'] = True

            aws_secret = resp['SecretList'][0]
            aws_secret_value = self._get_secret_value()
            yaml_secret_value = self.decrypt()

            if aws_secret_value != yaml_secret_value:
                changes['ChangesList'].append(
                    {
                        'Key': 'Value',
                        'HasChanges': True,
                        'Replaceable': True,
                        'Value': yaml_secret_value,
                        'OldValue': aws_secret_value
                    }
                )

            yaml_secret_description = self.description
            aws_secret_description = aws_secret.get('Description', '')

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

            if self.kms is not None and self.kms != aws_secret['KmsKeyId']:
                changes['ChangesList'].append(
                    {
                        'Key': 'KmsKeyId',
                        'HasChanges': True,
                        'Replaceable': True,
                        'Value': self.kms,
                        'OldValue': aws_secret['KmsKeyId']
                    }
                )

            yaml_tags = self.parse_tags()
            aws_tags = aws_secret['Tags']

            yaml_tags_sorted = sorted(yaml_tags, key=lambda k: k['Key'])
            aws_tags_sorted = sorted(aws_tags, key=lambda k: k['Key'])
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

    def _get_secret_value(self):
        client = self.session.client('secretsmanager')
        value = ''
        try:
            response = client.get_secret_value(
                SecretId=self.name
            )

            value = response['SecretString']
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise e

        return value
