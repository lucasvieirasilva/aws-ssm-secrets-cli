from botocore.exceptions import ClientError
from aws_secrets.miscellaneous import kms
from aws_secrets.miscellaneous import utils


def parse_yaml_parameter_value(session, param_data, kms_arn):
    yaml_param_value = str(param_data['value'])
    decrypt_on_deploy = param_data['decryptOnDeploy'] if 'decryptOnDeploy' in param_data else True

    if param_data['type'] == 'SecureString' and decrypt_on_deploy:
        yaml_param_value = kms.decrypt(
            session, yaml_param_value, kms_arn).decode('utf-8')

    return yaml_param_value


def needs_decrypt(param_data):
    return True if param_data['type'] == 'SecureString' else False


def get_parameter_details(session, param_data):
    ssm = session.client('ssm')
    resp = ssm.describe_parameters(
        ParameterFilters=[
            {
                'Key': 'Name',
                'Option': 'Equals',
                'Values': [param_data['name']]
            }
        ]
    )
    return resp


def check_if_description_has_changes(param_data, aws_param, changes):
    yaml_param_description = param_data['description'] if 'description' in param_data else ''
    aws_param_description = aws_param['Description'] if 'Description' in aws_param else ''

    if aws_param_description != yaml_param_description:
        changes['ChangesList'].append(
            {
                'Key': 'Description',
                'HasChanges': True,
                'Replaceable': True,
                'Value': yaml_param_description,
                'OldValue': aws_param_description
            }
        )


def check_if_value_has_changes(session, param_data, kms_arn, changes):
    decrypt = needs_decrypt(param_data)

    aws_param_value = get_parameter_value(
        session, param_data['name'], decrypt)

    yaml_param_value = parse_yaml_parameter_value(
        session, param_data, kms_arn)

    if aws_param_value != yaml_param_value:
        changes['ChangesList'].append(
            {
                'Key': 'Value',
                'HasChanges': True,
                'Replaceable': True,
                'Value': yaml_param_value,
                'OldValue': aws_param_value
            }
        )


def check_if_kms_has_changes(param_data, aws_param, changes):
    if 'kms' in param_data and param_data['kms'] != aws_param['KeyId']:
        changes['ChangesList'].append(
            {
                'Key': 'KeyId',
                'HasChanges': True,
                'Replaceable': True,
                'Value': param_data['kms'],
                'OldValue': aws_param['KeyId']
            }
        )


def check_if_type_has_changes(param_data, aws_param, changes):
    if param_data['type'] != aws_param['Type']:
        changes['ChangesList'].append(
            {
                'Key': 'Type',
                'HasChanges': True,
                'Replaceable': False,
                'Value': param_data['type'],
                'OldValue': aws_param['Type']
            }
        )


def check_if_tags_has_changes(session, param_data, changes):
    ssm = session.client('ssm')
    yaml_tags = utils.parse_tags(param_data)
    aws_tags = ssm.list_tags_for_resource(
        ResourceType='Parameter',
        ResourceId=param_data['name']
    )

    yaml_tags_sorted = sorted(yaml_tags, key=lambda k: k['Key'])
    aws_tags_sorted = sorted(aws_tags['TagList'], key=lambda k: k['Key'])
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


def get_parameter_changes(session, param_data, kms_arn):
    changes = {
        'Exists': False,
        'ChangesList': []
    }

    resp = get_parameter_details(session, param_data)

    if len(resp['Parameters']) > 0:
        changes['Exists'] = True

        aws_param = resp['Parameters'][0]

        check_if_value_has_changes(session, param_data, kms_arn, changes)

        check_if_description_has_changes(param_data, aws_param, changes)

        check_if_kms_has_changes(param_data, aws_param, changes)

        check_if_type_has_changes(param_data, aws_param, changes)

        check_if_tags_has_changes(session, param_data, changes)

    return changes


def get_parameter_value(session, name, decrypt):
    ssm = session.client('ssm')
    param_value = ''
    try:
        param_response = ssm.get_parameter(
            Name=name,
            WithDecryption=decrypt
        )

        param_value = param_response['Parameter']['Value']
    except ClientError as e:
        if e.response['Error']['Code'] != 'ParameterNotFound':
            raise e

    return param_value
