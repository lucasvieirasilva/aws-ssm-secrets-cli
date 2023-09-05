import yaml
from yaml.dumper import SafeDumper
from yaml.nodes import ScalarNode

from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.miscellaneous import cloudformation
from aws_secrets.miscellaneous.session import session


class OutputStackTag(yaml.YAMLObject):
    """
        Custom YAML tag class
        !cf_output tag calls the boto3 cloudformation get outputs API and resolve the output value

        Examples:
            >>> !cf_output <stack>.<output-name>
            >>> !cf_output <stack>.<output-name>.<aws-region>
            value: <stack-output-value>

        Args:
            value (`str`): value after `!cf_output` tag (e.g `!cf_output some` the value will be `some`)

        Attributes:
            value (`str`): value after `!cf_output` tag (e.g `!cf_output some` the value will be `some`)
    """
    yaml_tag = u'!cf_output'

    def __init__(self, value: str):
        self.stack = value

    def __repr__(self) -> str:
        """
            Resolve the CloudFormation stack ouput value

            Returns:
                `str`: stack output value
        """
        stack_args = self.stack.split('.')
        if len(stack_args) < 2 or len(stack_args) > 3:
            raise CLIError(
                (
                    f'value {self.stack} is invalid, the correct way to '
                    'fill this information is <stack-name>.<output-name> '
                    'or <stack-name>.<output-name>.<aws_region>'
                )
            )
        region = None
        stack_name = stack_args[0]
        output_name = stack_args[1]
        try:
            region = stack_args[2]
            session.aws_region = region
        except IndexError:
            pass

        return cloudformation.get_output_value(session(), stack_name, output_name)

    @classmethod
    def from_yaml(cls, _, node):
        return OutputStackTag(node.value)

    @classmethod
    def to_yaml(cls, dumper: SafeDumper, data) -> ScalarNode:
        return dumper.represent_scalar(cls.yaml_tag, data.stack)
