from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import utils


def parse_yaml_secret_value(session, secret_data, kms_arn):
    yaml_secret_value = str(secret_data['value'])
    yaml_secret_value = kms.decrypt(
        session, yaml_secret_value, kms_arn).decode('utf-8')

    return yaml_secret_value


def get_secret_changes(session, secret_data, kms_arn):
    changes = {
        'Exists': False,
        'ChangesList': []
    }
    client = session.client('secretsmanager')
    resp = client.list_secrets(
        Filters=[
            {
                'Key': 'name',
                'Values': [secret_data['name']]
            }
        ]
    )

    if len(resp['SecretList']) > 0:
        changes['Exists'] = True

        aws_secret = resp['SecretList'][0]
        aws_secret_value = get_secret_value(session, secret_data['name'])

        yaml_secret_value = parse_yaml_secret_value(
            session, secret_data, kms_arn)

        if aws_secret_value != yaml_secret_value:
            changes['ChangesList'].append(
                {
                    'Key': 'Value',
                    'HasChanges': True,
                    'Replaceable': True,
                    'Value': yaml_secret_value,
                    'OldValue': aws_secret_value
                }
            )

        yaml_secret_description = secret_data['description'] if 'description' in secret_data else ''
        aws_secret_description = aws_secret['Description'] if 'Description' in aws_secret else ''

        if aws_secret_description != yaml_secret_description:
            changes['ChangesList'].append(
                {
                    'Key': 'Description',
                    'HasChanges': True,
                    'Replaceable': True,
                    'Value': yaml_secret_description,
                    'OldValue': aws_secret_description
                }
            )

        if 'kms' in secret_data and secret_data['kms'] != aws_secret['KmsKeyId']:
            changes['ChangesList'].append(
                {
                    'Key': 'KmsKeyId',
                    'HasChanges': True,
                    'Replaceable': True,
                    'Value': secret_data['kms'],
                    'OldValue': aws_secret['KmsKeyId']
                }
            )

        yaml_tags = utils.parse_tags(secret_data)
        aws_tags = aws_secret['Tags']

        yaml_tags_sorted = sorted(yaml_tags, key=lambda k: k['Key'])
        aws_tags_sorted = sorted(aws_tags, key=lambda k: k['Key'])
        pairs = zip(yaml_tags_sorted, aws_tags_sorted)
        tags_changes = any(x != y for x, y in pairs) or len(yaml_tags_sorted) != len(aws_tags_sorted)

        if tags_changes:
            changes['ChangesList'].append(
                {
                    'Key': 'Tags',
                    'HasChanges': tags_changes,
                    'Replaceable': True,
                    'Value': yaml_tags_sorted,
                    'OldValue': aws_tags_sorted
                }
            )

    return changes


def get_secret_value(session, name):
    client = session.client('secretsmanager')
    value = ''
    try:
        response = client.get_secret_value(
            SecretId=name
        )

        value = response['SecretString']
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceNotFoundException':
            raise e

    return value
