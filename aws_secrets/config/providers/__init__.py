import abc
import fnmatch
import logging

import click
import six
from aws_secrets.miscellaneous import utils


@six.add_metaclass(abc.ABCMeta)
class BaseEntry:
    __metaclass__ = abc.ABCMeta

    def __init__(self, session, kms_arn, data, cipher_text=None) -> None:
        self._data = data

        self.logger = logging.getLogger(__name__)
        self.session = session
        self.kms_arn = kms_arn

        self.name = data['name']
        self.description = data.get('description', '')
        self.kms = data.get('kms', None)
        self.tags = data.get('tags', {})

        self.raw_value = data.get('value', None)
        self.cipher_text = cipher_text
        self.plain_text = None

    @abc.abstractmethod
    def decrypt(self) -> str:
        pass

    @abc.abstractmethod
    def encrypt(self):
        pass

    def parse_tags(self):
        tags = []
        for key in self.tags.keys():
            tags.append({
                'Key': key,
                'Value': self.tags[key]
            })
        return tags


@six.add_metaclass(abc.ABCMeta)
class BaseProvider:
    __metaclass__ = abc.ABCMeta

    def __init__(
        self,
        config
    ):
        self.logger = logging.getLogger(__name__)
        self.global_tags = config.global_tags
        self.session = config.session
        self.kms_arn = config.kms_arn
        self.config_data = config.data
        self.secrets_data = config.secrets_data
        self.entries = self.load_entries()

    def filter(self, filter_pattern):
        if filter_pattern:
            return list(filter(lambda e: fnmatch.fnmatch(e.name, filter_pattern), self.entries))
        else:
            return self.entries

    def merge_tags(self, resource: BaseEntry):
        resource.tags = {**self.global_tags, **resource.tags}

    def print_resource_name(self, resource, name):
        secret_msg = f"{resource}: [{name}]"
        click.echo(utils.repeat_to_length("=", len(secret_msg)))
        click.echo(secret_msg)

    def print_changes(self, changes):
        click.echo("--> Changes:")
        for change_item in changes['ChangesList']:
            click.echo(f"   --> {change_item['Key']}:")
            click.echo(
                f"          Old Value: {change_item['OldValue']}")
            click.echo(
                f"          New Value: {change_item['Value']}")

    def apply_non_replaceable_attrs(self, resource, changes, action):
        non_replaceable_attrs = list(filter(lambda change: change['Replaceable'] is False, changes['ChangesList']))
        if len(non_replaceable_attrs) > 0:
            attrs = ", ".join(list(map(lambda attr: attr['Key'], non_replaceable_attrs)))
            if click.confirm(
                    f"   --> These attributes [{attrs}] cannot be updated, would you like to re-create this resource?"):
                action(resource)
                return True
            else:
                click.echo("   --> Ignoring this resource")
                return None

        return False

    @abc.abstractmethod
    def deploy(self, filter_pattern, dry_run, confirm):
        pass

    @abc.abstractmethod
    def load_entries(self):
        pass

    @abc.abstractmethod
    def decrypt(self):
        pass

    def encrypt(self):
        self.logger.debug(f'Provider - {__name__} - Encrypting entries')
        result = []
        for item in self.entries:
            encrypted_value = item.encrypt()
            if encrypted_value:
                result.append({
                    'name': item.name,
                    'value': encrypted_value
                })

        return result

    @abc.abstractmethod
    def find(self, name) -> BaseEntry:
        pass

    @abc.abstractmethod
    def add(self, data):
        pass

    @abc.abstractmethod
    def update(self, data):
        pass

    @abc.abstractmethod
    def get_sensible_entries(self):
        pass
