import os
from pathlib import Path
from typing import Any, Dict

from aws_secrets.config.providers import BaseProvider
from aws_secrets.config.providers.secretsmanager.provider import \
    SecretsManagerProvider
from aws_secrets.config.providers.ssm.provider import SSMProvider
from aws_secrets.miscellaneous import session
from aws_secrets.yaml import yaml


class ConfigReader(object):
    """
    Config Reader handles the configuration and the secrets YAML files

    Also, abstract the encrypt/decrypt function using the Providers

    Args:
        config_file (`str`): configuration file path

    Attributes:
        data (`Dict[str, Any]`): configuration parsed YAML
        secrets_file_path (`str`): secrets YAML file path
        global_tags (`Dict[str, str]`): map of global tags of the config file
        secrets_data (`Dict[str, Any]`): secrets parsed YAML
        session (`Session`): boto3 session object
        kms_arn (`str`): Main Kms ARN
        providers (`Dict[str, BaseProvider]`): providers map
    """

    def __init__(self, config_file: str) -> None:
        super().__init__()
        self.config_file = config_file

        self.data = self.load_config()
        self.secrets_file_path = self._get_secrets_path()

        self.global_tags = self.data["tags"] if "tags" in self.data else {}
        self.secrets_data = self.load_secrets_config()

        self.session = session.session()
        self.kms_arn = self.get_kms_arn()
        self.encryption_sdk = self.data.get("encryption_sdk", "boto3")

        self.providers = self.load_providers()

    def get_provider(self, name: str) -> BaseProvider:
        """
        Get provider by name

        Supported names:
        - secrets
        - parameters

        Args:
            name (`str`): provider name

        Returns:
            `BaseProvider`: provider object
        """
        return self.providers[name]

    def _get_secrets_path(self) -> str:
        """
        Get Secret file path based on the environment file.

        Returns:
            `str`: secrets YAML file path
        """
        config_file_path = Path(self.config_file)
        config_filename = config_file_path.stem
        config_dir = str(config_file_path.parent)

        if "secrets_file" not in self.data:
            secrets_path = os.path.join(config_dir, f"{config_filename}.secrets.yaml")
            self.data["secrets_file"] = secrets_path
            return secrets_path
        else:
            return str(
                Path(os.path.join(config_dir, self.data["secrets_file"])).resolve()
            )

    def load_providers(self) -> Dict[str, BaseProvider]:
        """
        Load providers

        Returns:
            `Dict[str, BaseProvider]`: providers
        """
        providers = {
            "secrets": SecretsManagerProvider(self),
            "parameters": SSMProvider(self),
        }

        return providers

    def get_kms_arn(self) -> str:
        """
        Get main KMS Arn

        Returns:
            `str`: KMS ARN
        """
        return str(self.data["kms"]["arn"])

    def load_secrets_config(self) -> Dict[str, Any]:
        """
        Load secrets.yaml file to a dict object

        Returns:
            `Dict[str, Any]`: secrets dict object
        """
        secrets_data = {}

        if os.path.exists(self.secrets_file_path):
            with open(self.secrets_file_path, "r") as secrets:
                secrets_data = yaml.load(secrets.read())

        return secrets_data

    def load_config(self) -> Dict[str, Any]:
        """
        Load config YAML file to a dict object

        Returns:
            `Dict[str, Any]`: config dict object
        """
        with open(self.config_file, "r") as source:
            data = yaml.load(source.read())
        return data

    def decrypt(self) -> None:
        """
        Call decrypt function in all the providers
        """
        self.get_provider("secrets").decrypt()
        self.get_provider("parameters").decrypt()

    def encrypt(self) -> None:
        """
        Call encrypt function in all the providers and delete the `value` property from the secret entries
        """
        self.secrets_data = {
            "secrets": self.get_provider("secrets").encrypt(),
            "parameters": self.get_provider("parameters").encrypt(),
        }

        self._delete_plain_text_property()

    def _delete_plain_text_property(self) -> None:
        """
        Delete `value` property from the secrets entries

        For AWS Secrets Manager all the entries
        For AWS SSM Parameter all the parameter with `SecureString` type
        """
        all_sensetive_items = (
            self.get_provider("secrets").get_sensible_entries()
            + self.get_provider("parameters").get_sensible_entries()
        )

        for item in all_sensetive_items:
            if "value" in item and (
                isinstance(item["value"], str) or isinstance(item["value"], dict)
            ):
                del item["value"]

    def save(self) -> None:
        """
        Save config and secrets changes in the disk
        """
        with open(self.config_file, "w") as outfile:
            yaml.dump(self.data, outfile)

        with open(self.secrets_file_path, "w") as outfile:
            yaml.dump(self.secrets_data, outfile)
