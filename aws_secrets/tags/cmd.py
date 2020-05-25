import yaml
import subprocess
import os
from aws_secrets.miscellaneous.cloudformation import get_output_value
from aws_secrets.miscellaneous.session import session


class CmdTag(yaml.YAMLObject):
    yaml_tag = u'!cmd'

    def __init__(self, value):
        self.value = value

    def resolve_variables(self):
        if self.value.find("${") == -1:
            return

        variable = self.value[self.value.find("${")+2:self.value.find("}")]
        
        provider = variable.split(":")[0]
        value = variable.split(":")[1]
        stack_name = value.split(".")[0]
        output_name = value.split(".")[1]

        if provider == 'cf':
            output_value = get_output_value(session(), stack_name, output_name)

            self.value = self.value.replace(self.value[self.value.find("${"):self.value.find("}")+1], output_value)
        else:
            raise Exception(f'Provider {provider} is not supported')

        self.resolve_variables()

    def __repr__(self):
        self.resolve_variables()

        proc = subprocess.Popen(self.value.split(" "), stdout=subprocess.PIPE)
        output = proc.stdout.read()
        output_value = output.decode('utf-8').strip()
        return output_value

    @classmethod
    def from_yaml(cls, loader, node):
        return CmdTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.value)
