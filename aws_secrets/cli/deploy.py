import click
import yaml
import base64
import boto3
from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import session
from aws_secrets.miscellaneous.ssm import get_parameter_changes, parse_yaml_parameter_value
from aws_secrets.miscellaneous.secrets import get_secret_changes, parse_yaml_secret_value
from aws_secrets.miscellaneous import utils


@click.command(name='deploy')
@click.option('-e', '--env-file', help="Environment YAML file", type=click.Path(), required=True)
@click.option('--dry-run', help="Execution without apply the changes on the environment", is_flag=True)
@click.option('--confirm', help="Confirm prompt before apply the changes", is_flag=True)
@click.option('--profile', help="AWS Profile")
@click.option('--region', help="AWS Region")
def deploy(env_file, dry_run, confirm, profile, region):
    session.aws_profile = profile
    session.aws_region = region

    with open(env_file, 'r') as env:
        yaml_data = yaml.safe_load(env.read())

    global_tags = yaml_data['tags'] if 'tags' in yaml_data else {}
    
    _session = session.session()
    ssm = _session.client('ssm')
    secretsmanager = _session.client('secretsmanager')

    kms_arn = str(yaml_data['kms']['arn'])

    click.echo("Loading AWS Secrets Manager changes...")
    if 'secrets' in yaml_data:
        for secret in yaml_data['secrets']:
            merge_tags(secret, global_tags)
            
            changes = get_secret_changes(_session, secret, kms_arn)

            if not changes['Exists']:
                print_secret_name(secret['name'])
                click.echo("--> New Secret")

                if not dry_run:
                    if confirm:
                        if click.confirm("--> Would you to create this secret?"):
                            create_secret(_session, secret, kms_arn)
            else:
                if len(changes['ChangesList']) > 0:
                    print_secret_name(secret['name'])
                    click.echo(f"--> Changes:")
                    for change_item in changes['ChangesList']:
                        click.echo(f"   --> {change_item['Key']}:")
                        click.echo(
                            f"          Old Value: {change_item['OldValue']}")
                        click.echo(
                            f"          New Value: {change_item['Value']}")

                    non_replaceable_attrs = list(filter(
                        lambda change: change['Replaceable'] == False, changes['ChangesList']))

                    if not dry_run:
                        confirm_msg = "   --> Would you like to update this secret?"
                        if len(non_replaceable_attrs) > 0:
                            attrs = ", ".join(
                                list(map(lambda attr: attr['Key'], non_replaceable_attrs)))
                            if click.confirm(
                                    f"   --> These attributes [{attrs}] cannot be updated, do you would like to re-create this secret?"):
                                confirm_msg = "Would you like to recreate this secret?"
                                secretsmanager.delete_secret(
                                    SecretId=secret['name'],
                                    ForceDeleteWithoutRecovery=True
                                )
                                create_secret(_session, secret, kms_arn)
                            else:
                                click.echo(
                                    f"   --> Ignoring this secret")
                                continue
                        else:
                            if confirm:
                                if click.confirm(confirm_msg):
                                    secretsmanager.update_secret(
                                        SecretId=secret['name'],
                                        Description=secret['description'] if 'description' in secret else '',
                                        KmsKeyId=secret['kms'] if 'kms' in secret else '',
                                        SecretString=kms.decrypt(
                                            _session, secret['value'], kms_arn).decode('utf-8')
                                    )

                                    tags_change = next(
                                        (c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)
                                    aws_tags = tags_change['OldValue'] if tags_change is not None else [
                                    ]

                                    tags = utils.parse_tags(secret)
                                    if len(tags) > 0:
                                        tags_key = list(
                                            map(lambda tag: tag['Key'], aws_tags))
                                        secretsmanager.untag_resource(
                                            SecretId=secret['name'],
                                            TagKeys=tags_key
                                        )

                                        secretsmanager.tag_resource(
                                            SecretId=secret['name'],
                                            Tags=tags
                                        )

    click.echo("Loading SSM parameter changes...")
    if 'parameters' in yaml_data:
        for parameter in yaml_data['parameters']:
            merge_tags(parameter, global_tags)
            changes = get_parameter_changes(_session, parameter, kms_arn)

            if not changes['Exists']:
                print_parameter_name(parameter['name'])
                click.echo("--> New Parameter")

                if not dry_run:
                    if confirm:
                        if click.confirm("--> Would you to create this SSM parameter?"):
                            create_or_update_ssm_param(
                                _session, parameter, [], kms_arn)
            else:
                if len(changes['ChangesList']) > 0:
                    print_parameter_name(parameter['name'])
                    click.echo(f"--> Changes:")
                    for change_item in changes['ChangesList']:
                        click.echo(f"   --> {change_item['Key']}:")
                        click.echo(
                            f"          Old Value: {change_item['OldValue']}")
                        click.echo(
                            f"          New Value: {change_item['Value']}")

                    non_replaceable_attrs = list(filter(
                        lambda change: change['Replaceable'] == False, changes['ChangesList']))

                    if not dry_run:
                        confirm_msg = "   --> Would you like to update this SSM parameter?"
                        if len(non_replaceable_attrs) > 0:
                            attrs = ", ".join(
                                list(map(lambda attr: attr['Key'], non_replaceable_attrs)))
                            if click.confirm(
                                    f"   --> These attributes [{attrs}] cannot be updated, do you would like to re-create this SSM parameter?"):
                                confirm_msg = "Would you like to recreate this SSM parameter?"
                                ssm.delete_parameter(
                                    Name=parameter['name']
                                )
                            else:
                                click.echo(
                                    f"   --> Ignoring this SSM parameter")
                                continue

                        if confirm:
                            if click.confirm(confirm_msg):
                                tags_change = next(
                                    (c for c in changes['ChangesList'] if c['Key'] == 'Tags'), None)
                                aws_tags = tags_change['OldValue'] if tags_change is not None else [
                                ]

                                create_or_update_ssm_param(
                                    _session, parameter, aws_tags, kms_arn)


def create_secret(session, secret, kms_arn):
    secretsmanager = session.client('secretsmanager')
    secretsmanager.create_secret(
        Name=secret['name'],
        Description=secret['description'] if 'description' in secret else '',
        KmsKeyId=secret['kms'] if 'kms' in secret else '',
        SecretString=parse_yaml_secret_value(session, secret, kms_arn),
        Tags=utils.parse_tags(secret)
    )


def create_or_update_ssm_param(session, parameter, aws_tags, kms_arn):
    ssm = session.client('ssm')
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

    tags = utils.parse_tags(parameter)
    if len(tags) > 0:
        tags_key = list(map(lambda tag: tag['Key'], aws_tags))
        ssm.remove_tags_from_resource(
            ResourceType='Parameter',
            ResourceId=parameter['name'],
            TagKeys=tags_key
        )

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
