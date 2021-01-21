import yaml
import subprocess
from aws_secrets.miscellaneous import session
from aws_secrets.miscellaneous.cloudformation import get_output_value


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

        if provider == 'cf':
            stack_name = value.split(".")[0]
            output_name = value.split(".")[1]
            output_value = get_output_value(session.session(), stack_name, output_name)

            self.value = self.value.replace(self.value[self.value.find("${"):self.value.find("}")+1], output_value)
        elif provider == 'session':
            if value != 'profile' or value != 'region':
                raise Exception('Provider `session` just supports `profile` and `region` properties')

            output_value = ''

            if value == 'profile':
                output_value = session.aws_profile
            elif value == 'region':
                output_value = session.aws_region

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
