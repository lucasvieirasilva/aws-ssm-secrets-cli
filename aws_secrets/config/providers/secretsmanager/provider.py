import json
import click
from aws_secrets.config.providers import BaseProvider
from aws_secrets.config.providers.secretsmanager.entry import \
    SecretManagerEntry


class SecretsManagerProvider(BaseProvider):
    def __init__(self, config) -> None:
        super(SecretsManagerProvider, self).__init__(config)

    def load_entries(self):
        result = []
        self.logger.debug('Loading Secrets Manager entries')
        for param in self._get_data_entries():
            secret_data = next((p for p in self._get_secrets_entries() if p['name'] == param['name']), {})

            result.append(
                SecretManagerEntry(
                    session=self.session,
                    kms_arn=self.kms_arn,
                    data=param,
                    cipher_text=secret_data.get('value', None)
                )
            )

        return result

    def decrypt(self):
        self.logger.debug('Decrypting Secrets Manager entries')
        for item in self._get_data_entries():
            item_obj = next((p for p in self.entries if p.name == item['name']))
            decrypted_value = item_obj.decrypt()

            try:
                decrypted_value = json.loads(decrypted_value)
            except ValueError:
                pass

            item['value'] = decrypted_value

    def find(self, name):
        self.logger.debug(f'Finding Secrets Manager entries by name "{name}"')
        return next((e for e in self.entries if e.name == name), None)

    def add(self, data):
        self.logger.debug(f'Add "{data["name"]}" Secrets Manager entry')
        entry = SecretManagerEntry(
            session=self.session,
            kms_arn=self.kms_arn,
            data=data
        )
        self.entries.append(entry)
        self._get_data_entries().append(data)

        return entry

    def update(self, data):
        self.logger.debug(f'Updating "{data["name"]}" Secrets Manager entry')

        for idx, entry in enumerate(self.entries):
            if entry.name == data['name']:
                self.logger.debug('Updating entry in the entries list')
                self.entries[idx] = SecretManagerEntry(
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
        click.echo("Loading AWS Secrets Manager changes...")
        any_changes = False
        for secret in self.filter(filter_pattern):
            if self._deploy_secret(secret, dry_run, confirm):
                any_changes = True

        if any_changes is False:
            click.echo("no changes required")

    def _deploy_secret(
        self,
        secret: SecretManagerEntry,
        dry_run,
        confirm
    ):
        self.merge_tags(secret)
        changes = secret.changes()

        if not changes['Exists']:
            self.print_resource_name('Secret', secret.name)
            click.echo("--> New Secret")

            if not dry_run or (confirm and click.confirm("--> Would you to create this secret?")):
                secret.create()
                return True
        else:
            if len(changes['ChangesList']) > 0:
                self._apply_secret_changes(secret, changes, dry_run, confirm)
                return True

        return changes['Exists'] is False or len(changes['ChangesList']) > 0

    def _apply_secret_changes(
        self,
        secret: SecretManagerEntry,
        changes,
        dry_run,
        confirm
    ):
        self.print_resource_name('Secret', secret.name)
        self.print_changes(changes)

        if not dry_run:
            confirm_msg = "   --> Would you like to update this secret?"

            def non_replaceable_action(resource):
                secret.delete()
                secret.create()

            has_non_replaceable_changes = self.apply_non_replaceable_attrs(secret, changes, non_replaceable_action)

            if has_non_replaceable_changes is None:
                return

            if (has_non_replaceable_changes is False and confirm and click.confirm(confirm_msg)) \
                    or (has_non_replaceable_changes is False and confirm is False):
                secret.update(changes)

    def get_sensible_entries(self):
        return self._get_data_entries()

    def _get_secrets_entries(self):
        return self.secrets_data.get('secrets', [])

    def _get_data_entries(self):
        return self.config_data.get('secrets', [])
