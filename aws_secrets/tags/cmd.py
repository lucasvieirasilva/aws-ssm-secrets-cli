import logging
import subprocess

import click
from ruamel.yaml.constructor import ConstructorError
from ruamel.yaml.nodes import ScalarNode

from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.miscellaneous import cloudformation, session


class CmdTag:
    """
    Custom YAML tag class
    !cmd tag executes the command in the operation system and use the output console as value

    Providers:
        The providers work as variables in the `!cmd` command to replace some values
        - `cf`
        - `session`
        - `aws`

    Examples:
        >>> !cmd "echo 'hello'"
        value: `'hello'`

        >>> !cmd "echo '${cf:<stack>.<output-name>}'"
        value: `'<stack-output-value'`

    Args:
        value (`str`): value after `!cmd` tag (e.g `!cmd some` the value will be `some`)

    Attributes:
        value (`str`): value after `!cmd` tag (e.g `!cmd some` the value will be `some`)
        logger (`Logger`): logger instance
    """

    yaml_tag = "!cmd"

    def __init__(self, value: str):
        self.value = value
        self.logger = logging.getLogger(__name__)

    def resolve_variables(self) -> None:
        """
        Resolve variables in the tag value
        Variable pattern: `${<something>}`
        """
        if self.value.find("${") == -1:
            return

        variable = self.value[self.value.find("${") + 2: self.value.find("}")]

        provider = variable.split(":")[0]
        value = variable.split(":")[1]
        default_value = ""

        if "," in value:
            default_value = (
                value.split(",")[1].replace('"', "").replace("'", "").strip()
            )
            value = value.split(",")[0].strip()

        if provider == "cf":
            self.resolve_cf_provider(value, default_value)
        elif provider == "session":
            self.resolve_session_provider(value, default_value)
        elif provider == "aws":
            self.resolve_aws_provider(value, default_value)
        else:
            raise CLIError(f"Provider {provider} is not supported")

        self.resolve_variables()

    def resolve_aws_provider(self, value: str, default_value: str):
        """
        Resolve `aws` provider variables

        Args:
            value (`str`): raw command value
            default_value (`str`): default value for the provider

        Examples:
            >>> !cmd "${aws:profile}"
            "--profile <cli-profile>"

            >>> !cmd "${aws:profile, <default-value>}"
            "--profile <cli-profile or default-value>"

            >>> !cmd "${aws:profile}"
            "" If the `aws-secrets ... --profile <profile>` is not specified
        """
        self.check_aws_properties(value)

        output_value = ""

        if value == "profile":
            base_option = "--profile"
            if session.aws_profile:
                output_value = f"{base_option} {session.aws_profile}"
            elif default_value != "":
                output_value = f"{base_option} {default_value}"
        else:
            base_option = "--region"
            if session.aws_region:
                output_value = f"{base_option} {session.aws_region}"
            elif default_value != "":
                output_value = f"{base_option} {default_value}"

        self.resolve_value(output_value)

    def resolve_session_provider(self, value: str, default_value: str):
        """
        Resolve `session` provider variables

        Args:
            value (`str`): raw command value
            default_value (`str`): default value for the provider

        Examples:
            >>> !cmd "--profile ${session:profile}"
            "--profile <cli-profile>"

            >>> !cmd "--profile ${session:profile, <default-value>}"
            "--profile <cli-profile or default-value>"

            >>> !cmd "--profile ${session:profile}"
            "--profile " If the `aws-secrets ... --profile <profile>` is not specified
        """
        self.check_aws_properties(value)

        output_value = default_value

        if value == "profile" and session.aws_profile:
            output_value = session.aws_profile
        elif value == "region" and session.aws_region:
            output_value = session.aws_region

        self.resolve_value(output_value)

    def resolve_cf_provider(self, value: str, default_value: str):
        """
        Resolve `cf` provider variables

        Args:
            value (`str`): raw command value
            default_value (`str`): default value for the provider

        Examples:
            >>> !cmd "${cf:<stack>.<output>}"
            "<output-value>"
        """
        stack_name = value.split(".")[0]
        output_name = value.split(".")[1]
        output_value = cloudformation.get_output_value(
            session.session(), stack_name, output_name
        )

        if not output_value:
            output_value = default_value

        self.resolve_value(output_value)

    def resolve_value(self, output_value: str):
        """
        Resolve variable value

        Args:
            output_value (`str`): resolved value
        """
        self.value = self.value.replace(
            self.value[self.value.find("${"): self.value.find("}") + 1], output_value
        )

    def check_aws_properties(self, value: str):
        """
        Check AWS properties for the `aws` and `session` providers

        Args:
            value (`str`): tag value
        """
        allowed_values = ["profile", "region"]
        if value not in allowed_values:
            raise CLIError(
                f"Property `{value}` is not supported, "
                + f"provider `session` just supports {allowed_values} properties"
            )

    def __repr__(self) -> str:
        """
        Resolve the variables and execute the command in the operational system.

        Returns:
            `str` stdout output
        """
        self.resolve_variables()

        click.echo(f"Running command: {self.value}")

        process = subprocess.run(
            self.value.split(" "), stdout=subprocess.PIPE, encoding="utf-8"
        )

        return process.stdout.strip()

    @classmethod
    def from_yaml(cls, constructor, node):
        if isinstance(node, ScalarNode):
            return cls(node.value)
        raise ConstructorError(f"Error constructing YAML {cls.yaml_tag}")

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag, node.value)
