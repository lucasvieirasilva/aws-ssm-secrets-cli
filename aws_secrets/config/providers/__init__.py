import abc
import fnmatch
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import click
import six
from botocore.session import Session
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft3Validator, extend

from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.miscellaneous import utils
from aws_secrets.tags.cmd import CmdTag
from aws_secrets.tags.file import FileTag
from aws_secrets.tags.output_stack import OutputStackTag


@six.add_metaclass(abc.ABCMeta)
class BaseEntry:
    """
    Base entry class defines the Secret Provider entries behavior
    Encrypt/decrypt method definition.

    Args:
        session (`Session`): boto3 session
        kms_arn (`str`): KMS Key ARN
        data (`dict[str, Any]`): resource config properties
        cipher_text (`str, optional`): encrypted value

    Attributes:
        logger (`Logger`): logger instance
        session (`Session`): boto3 session
        kms_arn (`str`): KMS Key ARN
        name (`str`): resource name
        description (`str`): resource description
        kms (`str`, `optional`): resource custom Kms Key ARN or Id
        tags (`dict[str, str]`): resource tags
        raw_value (`Any`, `optional`): resource value, could be YAML tag Class, string value, or dict
        cipher_text (`str`, `optional`): resource encrypted value
    """

    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        session: Session,
        kms_arn: str,
        data: Dict[str, Any],
        provider: "BaseProvider",
        cipher_text: str = None,
    ) -> None:
        """
        Base class constructor

        Args:
            session (`Session`): boto3 session
            kms_arn (`str`): KMS Key ARN
            data (`dict[str, Any]`): resource config properties
            cipher_text (`str, optional`): encrypted value
        """
        self._data = data

        self.logger = logging.getLogger(__name__)
        self.session = session
        self.kms_arn = kms_arn

        self.name = data["name"]
        self.description = data.get("description", "")
        self.kms = data.get("kms", None)
        self.tags = data.get("tags", {})

        self.raw_value = data.get("value", None)
        self.cipher_text = cipher_text
        self.provider = provider

        self.validate_schema()

    def validate_schema(self) -> None:
        """
        validate JSON schema
        """

        def is_string_or_yaml_tag_type(_, instance):
            """
            Check if the type is string or one of the YAML tags:

            Supported tags:
                - !cmd
                - !file
                - !cf_output

            Args:
                _ (`Checker`): JSON schema checker object
                instance (`Any`): property value

            Returns:
                `bool`: if the instance is string or YAML tags
            """
            return (
                Draft3Validator.TYPE_CHECKER.is_type(instance, "string")
                or isinstance(instance, CmdTag)
                or isinstance(instance, FileTag)
                or isinstance(instance, OutputStackTag)
            )

        try:
            type_checker = Draft3Validator.TYPE_CHECKER.redefine(
                "string", is_string_or_yaml_tag_type
            )
            custom_validator = extend(Draft3Validator, type_checker=type_checker)
            validator = custom_validator(schema=self.schema())
            validator.validate(instance=self._data)
        except ValidationError as error:
            raise CLIError(f"Entry '{self.name}' is not valid, error: {str(error)}")

    @abc.abstractmethod
    def schema(self) -> dict:
        """
        Schema validation definition

        Returns:
            `dict`: JSON Schema format
        """

    def decrypt(self, format: bool = False) -> str:
        """
        Decrypt definition

        Returns:
            `str`: decrypted value
        """
        value = self._do_decrypt()
        return self._try_format_value(value) if format else value

    @abc.abstractmethod
    def _do_decrypt(self) -> str:
        """
        Decrypt definition

        Returns:
            `str`: decrypted value
        """

    @abc.abstractmethod
    def encrypt(self) -> Optional[str]:
        """
        Encrypt definition

        Returns:
            `str`, optional: encrypted value or None
        """

    def parse_tags(self) -> List[Dict[str, str]]:
        """
        Parse Tags from dict format to the AWS API Format:

        Returns:
            `List[dict[str, str]]`: list of tags

        Examples:
            >>> parse_tags({ 'origin': 'CLI' })
            [
                {
                    'Key': 'origin',
                    'Value': 'CLI'
                }
            ]
        """
        tags = []
        for key in self.tags.keys():
            tags.append({"Key": key, "Value": self.tags[key]})
        return tags

    def _try_format_value(self, value: str) -> str:
        try:
            # Try to pretty print the JSON output
            return json.dumps(json.loads(value), indent=2)
        except Exception:
            pass

        return value


@six.add_metaclass(abc.ABCMeta)
class BaseProvider:
    """
    Base provider class defines the behavior of the AWS Secrets providers

    Currently, SSM Parameters and AWS Secrets Manager

    The provider features are:
        - decrypt/encrypt
        - list/filter entries
        - find entries
        - add new entries
        - update entries
        - deploy entries to the AWS environment

    > Entries are the proper resource configuration, (e.g SSM Parameter or AWS Secrets Manager secret)

    Args:
        config (`ConfigReader`): configuration file reader handler

    Attributes:
        logger (`Logger`): logger instance
        global_tags (`Dict[str, str]`): map of global tags of the config file
        session (`Session`): boto3 session object
        kms_arn (`str`): Main Kms ARN
        config_data (`Dict[str, Any]`): configuration parsed YAML
        secrets_data (`Dict[str, Any]`): secrets parsed YAML
        entries (`List[BaseEntry]`): entries list
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        """
        class constructor

        Args:
            config (`ConfigReader`): configuration file reader handler
        """
        self.logger = logging.getLogger(__name__)
        self.global_tags = config.global_tags
        self.session = config.session
        self.kms_arn = config.kms_arn
        self.config_data = config.data
        self.secrets_data = config.secrets_data
        self.encryption_sdk = config.encryption_sdk
        self.entries = self.load_entries()

    def filter(self, filter_pattern: Optional[str]) -> List[BaseEntry]:
        """
        Filter entries based on a wildcard pattern

        Args:
            filter_pattern (`str`, optional): filter pattern

        Returns:
            `List[BaseEntry]`: list of filtered entries
        """
        if filter_pattern:
            return list(
                filter(lambda e: fnmatch.fnmatch(e.name, filter_pattern), self.entries)
            )
        else:
            return self.entries

    def merge_tags(self, resource: BaseEntry) -> None:
        """
        Merge global tags with the resource tags

        Args:
            resource (`BaseEntry`): resource object
        """
        resource.tags = {**self.global_tags, **resource.tags}

    def print_resource_name(self, resource: str, name: str) -> None:
        """
        Print in the CLI console the resource name with the separator line below

        Args:
            resource (`str`): resource type (e.g `Parameter` or `Secret`)
            name (`str`): resource name
        """
        secret_msg = f"{resource}: [{name}]"
        click.echo(utils.repeat_to_length("=", len(secret_msg)))
        click.echo(secret_msg)

    def print_changes(self, changes: Dict[str, Any]):
        """
        Print resource changes in the CLI console

        Args:
            changes (`Dict[str, Any]`): map of changes
        """
        click.echo("--> Changes:")
        for change_item in changes["ChangesList"]:
            click.echo(f"   --> {change_item['Key']}:")
            click.echo(f"          Old Value: {change_item['OldValue']}")
            click.echo(f"          New Value: {change_item['Value']}")

    def apply_non_replaceable_attrs(
        self,
        resource: BaseEntry,
        changes: Dict[str, Any],
        action: Callable[[BaseEntry], None],
    ) -> Optional[bool]:
        """
        Check if there are non replaceable attributes in the resource changes

        And If has call a generic action fuction

        Args:
            resource (`BaseEntry`): resource object
            changes (`Dict[str, Any]`): map of changes
            action (`Callable[[BaseEntry], None]`): action callback function

        Returns:
            `bool`, optional: if has non replaceable attributes or None
        """
        non_replaceable_attrs = list(
            filter(
                lambda change: change["Replaceable"] is False, changes["ChangesList"]
            )
        )
        if len(non_replaceable_attrs) > 0:
            attrs = ", ".join(
                list(map(lambda attr: attr["Key"], non_replaceable_attrs))
            )
            if click.confirm(
                f"   --> These attributes [{attrs}] cannot be updated, would you like to re-create this resource?"
            ):
                action(resource)
                return True
            else:
                click.echo("   --> Ignoring this resource")
                return None

        return False

    @abc.abstractmethod
    def deploy(
        self, filter_pattern: Optional[str], dry_run: bool, confirm: bool, show_diff: bool
    ) -> None:
        """
        Deploy abstract definition
        This function should be implemented with the provider deployment features, such as:
        - create new resources in the AWS environment
        - update attributes
        - recreate if it is necessary

        Args:
            filter_pattern (`Optional[str]`): resource filter pattern
            dry_run: (`bool`): dry run flag, just calculate the changes, but not apply them.
            confirm: (`bool`): CLI confirmation prompt for the changes.
        """

    @abc.abstractmethod
    def load_entries(self) -> List[BaseEntry]:
        """
        Load entries abstract definition
        This function should be implemented to load the provider entries (e.g list of ssm parameters or secrets)

        Returns:
            `List[BaseEntry]`: list of entries
        """

    @abc.abstractmethod
    def decrypt(self) -> None:
        """
        Decrypt entries abstract definition
        This function should be implemeted to decrypt all the secret entries in the provider.
        """

    def encrypt(self) -> List[Dict[str, str]]:
        """
        Encrypt all the secret entries in the provider and returns a list of them

        Returns:
            `List[Dict[str, str]]`: list of encrypted entries
        """
        self.logger.debug(f"Provider - {__name__} - Encrypting entries")
        result = []
        for item in self.entries:
            encrypted_value = item.encrypt()
            if encrypted_value:
                result.append({"name": item.name, "value": encrypted_value})

        return result

    @abc.abstractmethod
    def find(self, name: str) -> Optional[BaseEntry]:
        """
        Find entry abstract definition

        Args:
            name (`str`): entry name

        Returns:
            `BaseEntry`, optional: entry object or None
        """

    @abc.abstractmethod
    def add(self, data: Dict[str, Any]) -> BaseEntry:
        """
        Add new entry abstract definition

        Args:
            data (`Dict[str, Any]`): new entry data

        Returns:
            `BaseEntry`: entry object
        """

    @abc.abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Update an existing entry abstract definition

        Args:
            data (`Dict[str, Any]`): updated entry data
        """

    @abc.abstractmethod
    def get_sensible_entries(self) -> List[Dict[str, Any]]:
        """
        Get sensible entries based on the provider rules

        Returns:
            `List[Dict[str, Any]]`: list of sensible entries data
        """
