import os
from pathlib import Path

import yaml
from aws_secrets.config.providers import BaseProvider
from aws_secrets.config.providers.secretsmanager.provider import \
    SecretsManagerProvider
from aws_secrets.config.providers.ssm.provider import SSMProvider
from aws_secrets.miscellaneous import session


class ConfigReader(object):
    def __init__(self, config_file: str) -> None:
        super().__init__()
        self.config_file = config_file

        self.data = self.load_config()
        self.secrets_file_path = self._get_secrets_path()

        self.global_tags = self.data['tags'] if 'tags' in self.data else {}
        self.secrets_data = self.load_secrets_config()

        self.session = session.session()
        self.kms_arn = self.get_kms_arn()

        self.providers = self.load_providers()

    def get_provider(self, name: str) -> BaseProvider:
        return self.providers[name]

    def _get_secrets_path(self):
        """
            Get Secret file path based on the environment file.
        """
        if 'secrets_file' not in self.data:
            config_file_path = Path(self.config_file)
            config_filename = config_file_path.stem
            config_dir = str(config_file_path.parent)

            secrets_path = os.path.join(config_dir, f'{config_filename}.secrets.yaml')
            self.data['secrets_file'] = secrets_path

        return self.data['secrets_file']

    def load_providers(self):
        providers = {
            'secrets': SecretsManagerProvider(self),
            'parameters': SSMProvider(self)
        }

        return providers

    def get_kms_arn(self):
        return str(self.data['kms']['arn'])

    def load_secrets_config(self):
        secrets_data = {}

        if os.path.exists(self.secrets_file_path):
            with open(self.secrets_file_path, 'r') as secrets:
                secrets_data = yaml.safe_load(secrets.read())
        return secrets_data

    def load_config(self):
        with open(self.config_file, 'r') as source:
            data = yaml.safe_load(source.read())
        return data

    def decrypt(self):
        self.get_provider('secrets').decrypt()
        self.get_provider('parameters').decrypt()

    def encrypt(self):
        self.secrets_data = {
            'secrets': self.get_provider('secrets').encrypt(),
            'parameters': self.get_provider('parameters').encrypt()
        }

        self._delete_plain_text_property()

    def _delete_plain_text_property(self):
        all_sensetive_items = self.get_provider('secrets').get_sensible_entries() + \
            self.get_provider('parameters').get_sensible_entries()

        for item in all_sensetive_items:
            if 'value' in item and (isinstance(item['value'], str) or isinstance(item['value'], dict)):
                del item['value']

    def save(self):
        with open(self.config_file, 'w') as outfile:
            yaml.safe_dump(self.data, outfile)

        with open(self.secrets_file_path, 'w') as outfile:
            yaml.safe_dump(self.secrets_data, outfile)
