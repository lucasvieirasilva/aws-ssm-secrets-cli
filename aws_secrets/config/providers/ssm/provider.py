from typing import Any, Dict, List, Optional

import click

from aws_secrets.config.providers import BaseProvider
from aws_secrets.config.providers.ssm.entry import SSMParameterEntry
from aws_secrets.representers.literal import Literal


class SSMProvider(BaseProvider):
    """
    AWS SSM Parameter Provider

    This class handles the AWS SSM Parameter features:
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
        entries (`List[SSMParameterEntry]`): entries list
    """

    def __init__(self, config) -> None:
        super(SSMProvider, self).__init__(config)

    def load_entries(self) -> List[SSMParameterEntry]:
        """
        The SSM parameter entries
        location: config YAML file `parameters` list property

        Returns:
            `List[SSMParameterEntry]`: list of entries
        """
        result = []
        self.logger.debug("Loading SSM Parameter entries")
        for param in self._get_data_entries():
            secret_data = next(
                (p for p in self._get_secrets_entries() if p["name"] == param["name"]),
                {},
            )

            result.append(
                SSMParameterEntry(
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
        Decrypt the SSM parameter with `SecureString` type in the config file
        """
        self.logger.debug("Decrypting SSM Parameter entries")
        for item in self._get_data_entries():
            item_obj = self.find(item["name"])

            decrypted_value = item_obj.decrypt()
            if isinstance(decrypted_value, str) and "\n" in decrypted_value:
                item["value"] = Literal(decrypted_value)
            else:
                item["value"] = decrypted_value

    def find(self, name: str) -> Optional[SSMParameterEntry]:
        """
        Find an AWS SSM Parameter by name

        Args:
            name (`str`): entry name

        Returns:
            `SSMParameterEntry`, optional: parameter object or None
        """
        self.logger.debug(f'Finding SSM Parameter entries by name "{name}"')
        return next((e for e in self.entries if e.name == name), None)

    def add(self, data: Dict[str, Any]) -> SSMParameterEntry:
        """
        Add new AWS SSM Parameter

        Args:
            data (`Dict[str, Any]`): new parameter data

        Returns:
            `SSMParameterEntry`: parameter object
        """
        self.logger.debug(f'Add "{data["name"]}" SSM Parameter entry')
        entry = SSMParameterEntry(
            session=self.session, kms_arn=self.kms_arn, provider=self, data=data
        )
        self.entries.append(entry)
        self._get_data_entries().append(data)

        return entry

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update an existing parameter

        Args:
            data (`Dict[str, Any]`): updated parameter data
        """
        self.logger.debug(f'Updating "{data["name"]}" SSM Parameter entry')

        for idx, entry in enumerate(self.entries):
            if entry.name == data["name"]:
                self.logger.debug("Updating entry in the entries list")
                self.entries[idx] = SSMParameterEntry(
                    session=self.session, kms_arn=self.kms_arn, provider=self, data=data
                )

        data_entries = self._get_data_entries()
        for idx, item_data in enumerate(data_entries):
            if item_data["name"] == data["name"]:
                self.logger.debug("Updating entry data in the data entries list")
                data_entries[idx] = {**item_data, **data}

    def deploy(
        self,
        filter_pattern: Optional[str],
        dry_run: bool,
        confirm: bool,
        show_diff: bool,
    ) -> None:
        """
        Deploy all AWS SSM Paremeter changes

        Args:
            filter_pattern (`Optional[str]`): resource filter pattern
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
        """
        any_changes = False
        for parameter in self.filter(filter_pattern):
            if self._deploy_parameter(parameter, dry_run, confirm, show_diff):
                any_changes = True

        if any_changes is False:
            click.echo("no changes required")

    def _deploy_parameter(
        self,
        parameter: SSMParameterEntry,
        dry_run: bool,
        confirm: bool,
        show_diff: bool,
    ) -> bool:
        """
        Deploy the parameter changes

        Args:
            parameter (`SSMParameterEntry`): parameter entry object
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
            show_diff: (`bool`): show the diff of the changes

        Returns:
            `bool`: if changes are found.
        """
        self.merge_tags(parameter)
        changes = parameter.changes()

        if not changes["Exists"]:
            self.print_resource_name("Parameter", parameter.name)
            click.echo("--> New Parameter")

            if (
                not dry_run
                and confirm
                and click.confirm("--> Would you to create this SSM parameter?")
            ) or (not dry_run and confirm is False):
                parameter.create()
                return True
        else:
            if len(changes["ChangesList"]) > 0:
                self._deploy_parameter_changes(
                    parameter, changes, dry_run, confirm, show_diff
                )
                return True

        return changes["Exists"] is False or len(changes["ChangesList"]) > 0

    def _deploy_parameter_changes(
        self,
        parameter: SSMParameterEntry,
        changes: Dict[str, Any],
        dry_run: bool,
        confirm: bool,
        show_diff: bool,
    ) -> None:
        """
        Update an existing parameter on the AWS environment

        If the non replaceable attributes are found, recreate the resource instead of update

        Args:
            parameter (`SSMParameterEntry`): parameter entry object
            changes (`Dict[str, Any]`): map of changes
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
            show_diff: (`bool`): show the diff of the changes
        """
        self.print_resource_name("Parameter", parameter.name)
        if confirm or show_diff:
            self.print_changes(changes)
        else:
            click.echo(
                "--> Parameter has changes, "
                + "(use --show-diff to see the changes, not recommended when running in CI/CD)"
            )

        if not dry_run:
            confirm_msg = "   --> Would you like to update this SSM parameter?"

            def non_replaceable_action(param: SSMParameterEntry) -> None:
                param.delete()
                param.create()

            has_non_replaceable_changes = self.apply_non_replaceable_attrs(
                parameter, changes, non_replaceable_action
            )

            if has_non_replaceable_changes is None:
                return

            if (
                has_non_replaceable_changes is False
                and confirm
                and click.confirm(confirm_msg)
            ) or (has_non_replaceable_changes is False and confirm is False):
                parameter.update(changes)

    def get_sensible_entries(self) -> List[Dict[str, Any]]:
        """
        Get sensible entries, all parameters typed `SecureString`

        Returns:
            `List[Dict[str, Any]]`: list of sensible entries data
        """
        return list(
            filter(lambda p: p["type"] == "SecureString", self._get_data_entries())
        )

    def _get_secrets_entries(self) -> List[Dict[str, Any]]:
        """
        Get secrets config file entries

        Returns:
            `List[Dict[str, Any]]`: list of parameters data
        """
        if "parameters" not in self.secrets_data:
            self.secrets_data["parameters"] = []

        return self.secrets_data["parameters"]

    def _get_data_entries(self) -> List[Dict[str, Any]]:
        """
        Get the parsed config YAML parameters

        Returns:
            `List[Dict[str, Any]]`: list of parameters
        """
        if "parameters" not in self.config_data:
            self.config_data["parameters"] = []

        return self.config_data["parameters"]
