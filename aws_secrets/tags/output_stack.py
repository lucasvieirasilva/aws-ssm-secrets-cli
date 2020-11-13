import yaml
from aws_secrets.miscellaneous.cloudformation import get_output_value
from aws_secrets.miscellaneous.session import session


class OutputStackTag(yaml.YAMLObject):
    yaml_tag = u'!cf_output'

    def __init__(self, value):
        self.stack = value

    def __repr__(self):
        stack_args = self.stack.split('.')
        if len(stack_args) != 2:
            raise Exception(
                f'value {self.stack} is invalid, the correct way to ' +
                'fill this information is <stack-name>.<output-name>')

        stack_name = stack_args[0]
        output_name = stack_args[1]

        return get_output_value(session(), stack_name, output_name)

    @classmethod
    def from_yaml(cls, loader, node):
        return OutputStackTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.stack)
