import click
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
        default_value = ''

        if ',' in value:
            default_value = value.split(',')[1] \
                .replace('"', '') \
                .replace("'", '') \
                .strip()
            value = value.split(',')[0].strip()

        if provider == 'cf':
            self.resolve_cf_provider(value, default_value)
        elif provider == 'session':
            self.resolve_session_provider(value, default_value)
        elif provider == 'aws':
            self.resolve_aws_provider(value, default_value)
        else:
            raise RuntimeError(f'Provider {provider} is not supported')

        self.resolve_variables()

    def resolve_aws_provider(self, value, default_value):
        self.check_aws_properties(value)

        output_value = ''

        if value == 'profile':
            base_option = '--profile'
            if session.aws_profile:
                output_value = f'{base_option} {session.aws_profile}'
            elif default_value != '':
                output_value = f'{base_option} {default_value}'
        elif value == 'region':
            base_option = '--region'
            if session.aws_region:
                output_value = f'{base_option} {session.aws_region}'
            elif default_value != '':
                output_value = f'{base_option} {default_value}'

        self.resolve_value(output_value)

    def resolve_session_provider(self, value, default_value):
        self.check_aws_properties(value)

        output_value = default_value

        if value == 'profile' and session.aws_profile:
            output_value = session.aws_profile
        elif value == 'region' and session.aws_region:
            output_value = session.aws_region

        self.resolve_value(output_value)

    def resolve_cf_provider(self, value, default_value):
        stack_name = value.split(".")[0]
        output_name = value.split(".")[1]
        output_value = get_output_value(session.session(), stack_name, output_name)

        if not output_value:
            output_value = default_value

        self.resolve_value(output_value)

    def resolve_value(self, output_value):
        self.value = self.value.replace(self.value[self.value.find("${"):self.value.find("}")+1], output_value)

    def check_aws_properties(self, value):
        allowed_values = ['profile', 'region']
        if value not in allowed_values:
            raise RuntimeError(f'Property `{value}` is not supported, ' +
                               f'provider `session` just supports {allowed_values} properties')

    def __repr__(self):
        self.resolve_variables()

        click.echo(f"Running command: {self.value}")

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
