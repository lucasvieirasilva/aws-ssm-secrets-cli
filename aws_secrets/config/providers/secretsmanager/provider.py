import json
from typing import Any, Dict, List, Optional

import click

from aws_secrets.config.providers import BaseProvider
from aws_secrets.config.providers.secretsmanager.entry import \
    SecretManagerEntry


class SecretsManagerProvider(BaseProvider):
    """
    AWS Secrets Manager Provider

    This class handles the AWS Secrets Manager features:
    - deploy the changes
    - add new secrets
    - update existing secrets
    - decrypt/encrypt secrets

    Args:
        config (`ConfigReader`): configuration file reader handler

    Attributes:
        logger (`Logger`): logger instance
        global_tags (`Dict[str, str]`): map of global tags of the config file
        session (`Session`): boto3 session object
        kms_arn (`str`): Main Kms ARN
        config_data (`Dict[str, Any]`): configuration parsed YAML
        secrets_data (`Dict[str, Any]`): secrets parsed YAML
        entries (`List[SecretManagerEntry]`): entries list
    """

    def __init__(self, config) -> None:
        super(SecretsManagerProvider, self).__init__(config)

    def load_entries(self) -> List[SecretManagerEntry]:
        """
        the secrets entries
        location: config YAML file `secrets` list property

        Returns:
            `List[SecretManagerEntry]`: list of entries
        """
        result = []
        self.logger.debug("Loading Secrets Manager entries")
        for param in self._get_data_entries():
            secret_data = next(
                (p for p in self._get_secrets_entries() if p["name"] == param["name"]),
                {},
            )

            result.append(
                SecretManagerEntry(
                    session=self.session,
                    kms_arn=self.kms_arn,
                    data=param,
                    provider=self,
                    cipher_text=secret_data.get("value", None),
                )
            )

        return result

    def decrypt(self) -> None:
        """
        Decrypt all the secrets in the config file
        """
        self.logger.debug("Decrypting Secrets Manager entries")
        for item in self._get_data_entries():
            item_obj = self.find(item["name"])
            decrypted_value = item_obj.decrypt()

            try:
                decrypted_value = json.loads(decrypted_value)
            except Exception:
                pass

            item["value"] = decrypted_value

    def find(self, name: str) -> Optional[SecretManagerEntry]:
        """
        Find an AWS Secret Manager secret by name

        Args:
            name (`str`): entry name

        Returns:
            `SecretManagerEntry`, optional: secret object or None
        """
        self.logger.debug(f'Finding Secrets Manager entries by name "{name}"')
        return next((e for e in self.entries if e.name == name), None)

    def add(self, data: Dict[str, Any]) -> SecretManagerEntry:
        """
        Add new AWS Secret Manager secret

        Args:
            data (`Dict[str, Any]`): new secret data

        Returns:
            `SecretManagerEntry`: secret object
        """
        self.logger.debug(f'Add "{data["name"]}" Secrets Manager entry')
        entry = SecretManagerEntry(
            session=self.session, kms_arn=self.kms_arn, provider=self, data=data
        )
        self.entries.append(entry)
        self._get_data_entries().append(data)
        self._get_secrets_entries()

        return entry

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update an existing secret

        Args:
            data (`Dict[str, Any]`): updated secret data
        """
        self.logger.debug(f'Updating "{data["name"]}" Secrets Manager entry')

        for idx, entry in enumerate(self.entries):
            if entry.name == data["name"]:
                self.logger.debug("Updating entry in the entries list")
                self.entries[idx] = SecretManagerEntry(
                    session=self.session, kms_arn=self.kms_arn, provider=self, data=data
                )

        data_entries = self._get_data_entries()
        for idx, item_data in enumerate(data_entries):
            if item_data["name"] == data["name"]:
                self.logger.debug("Updating entry data in the data entries list")
                data_entries[idx] = {**data_entries[idx], **data}

    def deploy(
        self,
        filter_pattern: Optional[str],
        dry_run: bool,
        confirm: bool,
        show_diff: bool,
    ) -> None:
        """
        Deploy all AWS Secrets Manager secrets changes

        Args:
            filter_pattern (`Optional[str]`): resource filter pattern
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
        """
        click.echo("Loading AWS Secrets Manager changes...")
        any_changes = False
        for secret in self.filter(filter_pattern):
            if self._deploy_secret(secret, dry_run, confirm, show_diff):
                any_changes = True

        if any_changes is False:
            click.echo("no changes required")

    def _deploy_secret(
        self, secret: SecretManagerEntry, dry_run: bool, confirm: bool, show_diff: bool
    ) -> bool:
        """
        Deploy a secret changes

        Args:
            secret (`SecretManagerEntry`): Secret entry object
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
            show_diff: (`bool`): Show the diff of the changes

        Returns:
            `bool`: if changes are found.
        """
        self.merge_tags(secret)
        changes = secret.changes()

        if not changes["Exists"]:
            self.print_resource_name("Secret", secret.name)
            click.echo("--> New Secret")

            if (
                not dry_run
                and confirm
                and click.confirm("--> Would you to create this secret?")
            ) or (not dry_run and confirm is False):
                secret.create()
                return True
        else:
            if len(changes["ChangesList"]) > 0:
                self._apply_secret_changes(secret, changes, dry_run, confirm, show_diff)
                return True

        return changes["Exists"] is False or len(changes["ChangesList"]) > 0

    def _apply_secret_changes(
        self,
        secret: SecretManagerEntry,
        changes: Dict[str, Any],
        dry_run: bool,
        confirm: bool,
        show_diff: bool,
    ) -> None:
        """
        Update an existing secret on the AWS environment

        Args:
            secret (`SecretManagerEntry`): Secret entry object
            changes (`Dict[str, Any]`): map of changes
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
            show_diff: (`bool`): Show the diff of the changes
        """
        self.print_resource_name("Secret", secret.name)
        if confirm or show_diff:
            self.print_changes(changes)
        else:
            click.echo(
                "--> Secret has changes, "
                + "(use --show-diff to see the changes, not recommended when running in CI/CD)"
            )

        if not dry_run:
            confirm_msg = "   --> Would you like to update this secret?"
            if (confirm and click.confirm(confirm_msg)) or confirm is False:
                secret.update(changes)

    def get_sensible_entries(self) -> List[Dict[str, Any]]:
        """
        Get sensible entries, in the AWS Secrets Manager case all the entries

        Returns:
            `List[Dict[str, Any]]`: list of sensible entries data
        """
        return self._get_data_entries()

    def _get_secrets_entries(self) -> List[Dict[str, Any]]:
        """
        Get secrets config file entries

        Returns:
            `List[Dict[str, Any]]`: list of secrets
        """
        if "secrets" not in self.secrets_data:
            self.secrets_data["secrets"] = []

        return self.secrets_data.get("secrets", [])

    def _get_data_entries(self) -> List[Dict[str, Any]]:
        """
        Get the parsed config YAML secrets

        Returns:
            `List[Dict[str, Any]]`: list of secrets
        """
        if "secrets" not in self.config_data:
            self.config_data["secrets"] = []

        return self.config_data.get("secrets", [])
