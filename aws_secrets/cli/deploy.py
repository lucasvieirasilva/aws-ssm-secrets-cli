import click
import yaml
import fnmatch
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session
from aws_secrets.miscellaneous.ssm import get_parameter_changes, parse_yaml_parameter_value
from aws_secrets.miscellaneous.secrets import get_secret_changes, parse_yaml_secret_value
from aws_secrets.miscellaneous import utils


@click.command(name='deploy')
@click.option('-e', '--env-file', help="Environment YAML file", type=click.Path(), required=True)
@click.option('--filter-pattern', help="Filter Pattern", type=str)
@click.option('--dry-run', help="Execution without apply the changes on the environment", is_flag=True)
@click.option('--confirm', help="Confirm prompt before apply the changes", is_flag=True)
@click.option('--only-secrets', help="Deploy only AWS Secrets", is_flag=True)
@click.option('--only-parameters', help="Deploy only SSM Parameters", is_flag=True)
@click.option('--profile', help="AWS Profile")
@click.option('--region', help="AWS Region")
def deploy(env_file, filter_pattern, dry_run, confirm, only_secrets, only_parameters, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    global_tags = yaml_data['tags'] if 'tags' in yaml_data else {}
    _session = session.session()
    kms_arn = str(yaml_data['kms']['arn'])

    process_secrets(_session, yaml_data, global_tags, filter_pattern, kms_arn,
                    dry_run, confirm, only_secrets, only_parameters)
    process_parameters(_session, yaml_data, global_tags, filter_pattern, kms_arn,
                       dry_run, confirm, only_secrets, only_parameters)


def filter_resources(filter_pattern, resources):
    resources = list(filter(lambda resource: fnmatch.fnmatch(
        resource['name'], filter_pattern), resources))
    return resources


def get_secrets(yaml_data, filter_pattern):
    secrets = yaml_data['secrets']
    if filter_pattern:
        secrets = filter_resources(filter_pattern, secrets)

    return secrets


def process_secrets(session, yaml_data, global_tags, filter_pattern, kms_arn, dry_run, confirm, only_secrets, only_parameters):
    if only_secrets == True or (only_secrets == False and only_parameters == False):
        click.echo("Loading AWS Secrets Manager changes...")
        any_changes = False
        if 'secrets' in yaml_data:
            for secret in get_secrets(yaml_data, filter_pattern):
                if deploy_secret(
                        session, secret, global_tags, kms_arn, dry_run, confirm):
                    any_changes = True

        if any_changes == False:
            click.echo("no changes required")


def get_parameters(yaml_data, filter_pattern):
    parameters = yaml_data['parameters']
    if filter_pattern:
        parameters = filter_resources(filter_pattern, parameters)

    return parameters


def process_parameters(session, yaml_data, global_tags, filter_pattern, kms_arn, dry_run, confirm, only_secrets, only_parameters):
    if only_parameters == True or (only_secrets == False and only_parameters == False):
        click.echo("Loading SSM parameter changes...")
        any_changes = False
        if 'parameters' in yaml_data:
            for parameter in get_parameters(yaml_data, filter_pattern):
                if deploy_parameter(
                        session, parameter, global_tags, kms_arn, dry_run, confirm):
                    any_changes = True

        if any_changes == False:
            click.echo("no changes required")


def add_tags_to_secret(session, secret, tags):
    secretsmanager = session.client('secretsmanager')

    secretsmanager.tag_resource(
        SecretId=secret['name'],
        Tags=tags
    )


def remove_tags_from_secret(session, secret, aws_tags):
    secretsmanager = session.client('secretsmanager')

    tags_key = list(
        map(lambda tag: tag['Key'], aws_tags))
    secretsmanager.untag_resource(
        SecretId=secret['name'],
        TagKeys=tags_key
    )


def delete_secret(session, secret):
    secretsmanager = session.client('secretsmanager')

    secretsmanager.delete_secret(
        SecretId=secret['name'],
        ForceDeleteWithoutRecovery=True
    )


def update_secret(session, secret, kms_arn):
    secretsmanager = session.client('secretsmanager')

    secretsmanager.update_secret(
        SecretId=secret['name'],
        Description=secret['description'] if 'description' in secret else '',
        KmsKeyId=secret['kms'] if 'kms' in secret else '',
        SecretString=kms.decrypt(
            session, secret['value'], kms_arn).decode('utf-8')
    )


def process_secret_changes(session, secret, changes, dry_run, confirm, kms_arn):
    print_secret_name(secret['name'])
    print_changes(changes)

    if not dry_run:
        confirm_msg = "   --> Would you like to update this secret?"

        def non_replaceable_action(resource):
            delete_secret(session, resource)
            create_secret(session, resource, kms_arn)

        has_non_replaceable_changes = process_non_replaceable_attrs(
            session, secret, changes, non_replaceable_action)

        if has_non_replaceable_changes == None:
            return

        if (has_non_replaceable_changes == False and confirm and click.confirm(confirm_msg)) or (has_non_replaceable_changes == False and confirm == False):
            update_secret(session, secret, kms_arn)

            tags_change = next(
                (c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)
            aws_tags = tags_change['OldValue'] if tags_change is not None else [
            ]

            remove_tags_from_secret(session, secret, aws_tags)

            tags = utils.parse_tags(secret)
            if len(tags) > 0:
                add_tags_to_secret(session, secret, tags)


def deploy_secret(session, secret, global_tags, kms_arn, dry_run, confirm):
    merge_tags(secret, global_tags)

    changes = get_secret_changes(session, secret, kms_arn)

    if not changes['Exists']:
        print_secret_name(secret['name'])
        click.echo("--> New Secret")

        if not dry_run and confirm and click.confirm("--> Would you to create this secret?"):
            create_secret(session, secret, kms_arn)
            return True
    else:
        if len(changes['ChangesList']) > 0:
            process_secret_changes(
                session, secret, changes, dry_run, confirm, kms_arn)
            return True

    return False


def print_changes(changes):
    click.echo(f"--> Changes:")
    for change_item in changes['ChangesList']:
        click.echo(f"   --> {change_item['Key']}:")
        click.echo(
            f"          Old Value: {change_item['OldValue']}")
        click.echo(
            f"          New Value: {change_item['Value']}")


def process_non_replaceable_attrs(session, resource, changes, action):
    non_replaceable_attrs = list(filter(
        lambda change: change['Replaceable'] == False, changes['ChangesList']))
    if len(non_replaceable_attrs) > 0:
        attrs = ", ".join(
            list(map(lambda attr: attr['Key'], non_replaceable_attrs)))
        if click.confirm(
                f"   --> These attributes [{attrs}] cannot be updated, would you like to re-create this resource?"):
            action(resource)
            return True
        else:
            click.echo(
                f"   --> Ignoring this resource")
            return None

    return False


def deploy_parameter_changes(session, parameter, changes, kms_arn, dry_run, confirm):
    print_parameter_name(parameter['name'])
    print_changes(changes)

    if not dry_run:
        confirm_msg = "   --> Would you like to update this SSM parameter?"

        def non_replaceable_action(param):
            ssm = session.client('ssm')
            ssm.delete_parameter(
                Name=param['name']
            )

        has_non_replaceable_changes = process_non_replaceable_attrs(
            session, parameter, changes, non_replaceable_action)

        if has_non_replaceable_changes == None:
            return

        if (has_non_replaceable_changes == False and confirm and click.confirm(confirm_msg)) or confirm == False:
            create_or_update_ssm_param(
                session, parameter, changes, kms_arn)


def deploy_parameter(session, parameter, global_tags, kms_arn, dry_run, confirm):
    merge_tags(parameter, global_tags)
    changes = get_parameter_changes(session, parameter, kms_arn)

    if not changes['Exists']:
        print_parameter_name(parameter['name'])
        click.echo("--> New Parameter")

        if (not dry_run and confirm and click.confirm("--> Would you to create this SSM parameter?")) or (not dry_run and confirm == False):
            create_or_update_ssm_param(
                session, parameter, changes, kms_arn)
            return True
    else:
        if len(changes['ChangesList']) > 0:
            deploy_parameter_changes(
                session, parameter, changes, kms_arn, dry_run, confirm)
            return True

    return False


def create_secret(session, secret, kms_arn):
    secretsmanager = session.client('secretsmanager')
    secretsmanager.create_secret(
        Name=secret['name'],
        Description=secret['description'] if 'description' in secret else '',
        KmsKeyId=secret['kms'] if 'kms' in secret else '',
        SecretString=parse_yaml_secret_value(session, secret, kms_arn),
        Tags=utils.parse_tags(secret)
    )


def create_or_update_ssm_param(session, parameter, changes, kms_arn):
    ssm = session.client('ssm')

    if changes['Exists'] == False or next((c for c in changes['ChangesList'] if c['Key'] != 'Tags'), None):
        put_parameter_args = {
            'Name': parameter['name'],
            'Description': parameter['description'] if 'description' in parameter else '',
            'Value': parse_yaml_parameter_value(session, parameter, kms_arn),
            'Type': parameter['type'],
            'Overwrite': True
        }

        if 'kms' in parameter:
            put_parameter_args['KeyId'] = parameter['kms']

        ssm.put_parameter(**put_parameter_args)

    tags_change = next(
        (c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)

    if tags_change:
        aws_tags = tags_change['OldValue'] if tags_change is not None else [
        ]
        tags_key = list(map(lambda tag: tag['Key'], aws_tags))
        ssm.remove_tags_from_resource(
            ResourceType='Parameter',
            ResourceId=parameter['name'],
            TagKeys=tags_key
        )

        tags = utils.parse_tags(parameter)
        if len(tags) > 0:
            ssm.add_tags_to_resource(
                ResourceType='Parameter',
                ResourceId=parameter['name'],
                Tags=tags
            )


def print_parameter_name(name):
    parameter_msg = f"Parameter: [{name}]"
    click.echo(utils.repeat_to_length("=", len(parameter_msg)))
    click.echo(parameter_msg)


def print_secret_name(name):
    secret_msg = f"Secret: [{name}]"
    click.echo(utils.repeat_to_length("=", len(secret_msg)))
    click.echo(secret_msg)


def merge_tags(resource, global_tags):
    if 'tags' in resource:
        resource['tags'] = {**global_tags, **resource['tags']}
    else:
        resource['tags'] = global_tags
