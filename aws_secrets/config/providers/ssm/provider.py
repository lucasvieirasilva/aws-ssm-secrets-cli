import click
from aws_secrets.config.providers import BaseEntry, BaseProvider
from aws_secrets.config.providers.ssm.entry import SSMParameterEntry
from aws_secrets.representers.literal import Literal


class SSMProvider(BaseProvider):
    def __init__(self, config) -> None:
        super(SSMProvider, self).__init__(config)

    def load_entries(self):
        result = []
        self.logger.debug('Loading SSM Parameter entries')
        for param in self._get_data_entries():
            secret_data = next((p for p in self._get_secrets_entries() if p['name'] == param['name']), {})

            result.append(
                SSMParameterEntry(
                    session=self.session,
                    kms_arn=self.kms_arn,
                    data=param,
                    cipher_text=secret_data.get('value', None)
                )
            )

        return result

    def decrypt(self):
        self.logger.debug('Decrypting SSM Parameter entries')
        for item in self._get_data_entries():
            item_obj = next((p for p in self.entries if p.name == item['name']))

            decrypted_value = item_obj.decrypt()
            if decrypted_value:
                if '\n' in decrypted_value:
                    item['value'] = Literal(decrypted_value)
                else:
                    item['value'] = decrypted_value

    def find(self, name) -> BaseEntry:
        self.logger.debug(f'Finding SSM Parameter entries by name "{name}"')
        return next((e for e in self.entries if e.name == name), None)

    def add(self, data):
        self.logger.debug(f'Add "{data["name"]}" SSM Parameter entry')
        entry = SSMParameterEntry(
            session=self.session,
            kms_arn=self.kms_arn,
            data=data
        )
        self.entries.append(entry)
        self._get_data_entries().append(data)

        return entry

    def update(self, data):
        self.logger.debug(f'Updating "{data["name"]}" SSM Parameter entry')

        for idx, entry in enumerate(self.entries):
            if entry.name == data['name']:
                self.logger.debug('Updating entry in the entries list')
                self.entries[idx] = SSMParameterEntry(
                    session=self.session,
                    kms_arn=self.kms_arn,
                    data=data
                )

        data_entries = self._get_data_entries()
        for idx, item_data in enumerate(data_entries):
            if item_data['name'] == data['name']:
                self.logger.debug('Updating entry data in the data entries list')
                data_entries[idx] = data

    def deploy(self, filter_pattern, dry_run, confirm):
        any_changes = False
        for parameter in self.filter(filter_pattern):
            if self._deploy_parameter(parameter, dry_run, confirm):
                any_changes = True

        if any_changes is False:
            click.echo("no changes required")

    def _deploy_parameter(
        self,
        parameter: SSMParameterEntry,
        dry_run,
        confirm
    ):
        self.merge_tags(parameter)
        changes = parameter.changes()

        if not changes['Exists']:
            self.print_resource_name('Parameter', parameter.name)
            click.echo("--> New Parameter")

            if (not dry_run and confirm and
                    click.confirm("--> Would you to create this SSM parameter?")) or \
                    (not dry_run and confirm is False):
                parameter.create()
                return True
        else:
            if len(changes['ChangesList']) > 0:
                self._deploy_parameter_changes(parameter, changes, dry_run, confirm)
                return True

        return changes['Exists'] is False or len(changes['ChangesList']) > 0

    def _deploy_parameter_changes(
        self,
        parameter: SSMParameterEntry,
        changes,
        dry_run,
        confirm
    ):
        self.print_resource_name('Parameter', parameter.name)
        self.print_changes(changes)

        if not dry_run:
            confirm_msg = "   --> Would you like to update this SSM parameter?"

            def non_replaceable_action(param):
                parameter.delete()

            has_non_replaceable_changes = self.apply_non_replaceable_attrs(parameter, changes, non_replaceable_action)

            if has_non_replaceable_changes is None:
                return

            if (has_non_replaceable_changes is False and confirm and click.confirm(confirm_msg)) or confirm is False:
                parameter.update(changes)

    def get_sensible_entries(self):
        return list(filter(lambda p: p['type'] == 'SecureString', self._get_data_entries()))

    def _get_secrets_entries(self):
        return self.secrets_data.get('parameters', [])

    def _get_data_entries(self):
        if 'parameters' not in self.config_data:
            self.config_data['parameters'] = []

        return self.config_data['parameters']
