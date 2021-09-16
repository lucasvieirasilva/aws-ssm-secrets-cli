from unittest.mock import patch

import boto3
import pytest
from botocore.stub import Stubber

from aws_secrets.config.providers.ssm.entry import SSMParameterEntry
from aws_secrets.helpers.catch_exceptions import CLIError

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
KEY_ARN1 = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab1'


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt_secure_string(mock_encrypt):
    """
        Should encrypt the raw value
    """

    mock_encrypt.return_value = b'SecretData'

    session = boto3.Session(region_name='us-east-1')

    entry = SSMParameterEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'ssm-param',
            'type': 'SecureString',
            'value': 'MyPlainText'
        },
        cipher_text=None
    )

    assert entry.encrypt() == 'SecretData'
    mock_encrypt.assert_called_once_with(session, 'MyPlainText', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt_secure_string_already_encrypted(mock_encrypt):
    """
        Should not encrypt the raw value when the value is already encrypted
    """

    session = boto3.Session(region_name='us-east-1')

    entry = SSMParameterEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'ssm-param',
            'type': 'SecureString'
        },
        cipher_text='SecretData'
    )

    assert entry.encrypt() == 'SecretData'
    mock_encrypt.assert_not_called()


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt_invalid_type(mock_encrypt):
    """
        Should not encrypt when the type is invalid
    """

    session = boto3.Session(region_name='us-east-1')

    with pytest.raises(CLIError) as error:
        SSMParameterEntry(
            session=session,
            kms_arn=KEY_ARN,
            data={
                'name': 'ssm-param',
                'type': 'Invalid'
            },
            cipher_text='SecretData'
        )

        assert "'Invalid' is not one of ['String', 'SecureString']" in str(error.value)
        mock_encrypt.assert_not_called()


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_decrypt_secure_string(mock_decrypt):
    """
        Should decrypt the cipher text
    """

    mock_decrypt.return_value = b'PlainTextData'

    session = boto3.Session(region_name='us-east-1')

    entry = SSMParameterEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'ssm-param',
            'type': 'SecureString'
        },
        cipher_text='SecretData'
    )

    assert entry.decrypt() == 'PlainTextData'
    mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_decrypt_secure_string_with_value_data(mock_decrypt):
    """
        Should decrypt the cipher text
    """

    mock_decrypt.return_value = b'PlainTextData'

    session = boto3.Session(region_name='us-east-1')

    entry = SSMParameterEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'ssm-param',
            'type': 'SecureString',
            'value': 'SecretData'
        },
        cipher_text=None
    )

    assert entry.decrypt() == 'PlainTextData'
    mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_decrypt_string_type(mock_decrypt):
    """
        Should not decrypt when the type is not SecureString
    """

    mock_decrypt.return_value = b'PlainTextData'

    session = boto3.Session(region_name='us-east-1')

    entry = SSMParameterEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'ssm-param',
            'type': 'String',
            'value': 'PlainTextData'
        },
        cipher_text=None
    )

    assert entry.decrypt() == 'PlainTextData'
    mock_decrypt.assert_not_called()


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_create_default_kms(mock_decrypt):
    """
        Should create the SSM parameter in the AWS environment
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Tags': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type
                }
            )

            entry.create()
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_create_custom_kms(mock_decrypt):
    """
        Should create the SSM parameter in the AWS environment
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'KeyId': KEY_ARN,
                'Tags': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'kms': KEY_ARN
                }
            )

            entry.create()
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_update_default_kms_without_tag_changes(mock_decrypt):
    """
        Should update the SSM parameter in the AWS environment without tag changes
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Overwrite': True
            })
            stubber.add_response('remove_tags_from_resource', {}, {
                'ResourceType': 'Parameter',
                'ResourceId': name,
                'TagKeys': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type
                }
            )

            entry.update({
                'ChangesList': []
            })
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_update_custom_kms_without_tag_changes(mock_decrypt):
    """
        Should update the SSM parameter in the AWS environment without tag changes
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'KeyId': KEY_ARN,
                'Overwrite': True
            })
            stubber.add_response('remove_tags_from_resource', {}, {
                'ResourceType': 'Parameter',
                'ResourceId': name,
                'TagKeys': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'kms': KEY_ARN
                }
            )

            entry.update({
                'ChangesList': []
            })
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_update_default_kms_with_tag_changes(mock_decrypt):
    """
        Should update the SSM parameter in the AWS environment with tag changes
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Overwrite': True
            })
            stubber.add_response('remove_tags_from_resource', {}, {
                'ResourceType': 'Parameter',
                'ResourceId': name,
                'TagKeys': ['Test']
            })
            stubber.add_response('add_tags_to_resource', {}, {
                'ResourceType': 'Parameter',
                'ResourceId': name,
                'Tags': [{
                    'Key': 'Test',
                    'Value': 'New'
                }]
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'tags': {
                        'Test': 'New'
                    }
                }
            )

            entry.update({
                'ChangesList': [{
                    'Key': 'Tags',
                    'OldValue': [{
                        'Key': 'Test',
                        'Value': 'Old'
                    }]
                }]
            })
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


def test_delete():
    """
        Should delete the SSM parameter in the AWS environment
    """
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('delete_parameter', {}, {
                'Name': name
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type
                }
            )

            entry.delete()
            assert True


def test_calculate_changes_with_parameter_not_exists():
    """
        Should calculate the changes between AWS resource and local resource

        Scenario:
            - Parameter not exists
    """
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': []
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': [name]
                    }
                ]
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type
                }
            )

            assert entry.changes() == {
                'Exists': False,
                'ChangesList': []
            }


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_calculate_changes_with_changes(mock_decrypt):
    """
        Should calculate the changes between AWS resource and local resource

        Scenario:
            - Parameter exists
            - Value changed
            - Description changed
            - Type changed
            - Tier changed
            - Kms changed
            - Tags changed
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': name,
                    'Description': f'{description} CHANGED',
                    'Type': 'String',
                    'KeyId': KEY_ARN1,
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': [name]
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'AWSData'
                }
            }, {
                'Name': name,
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': [{
                    'Key': 'Test',
                    'Value': 'Old'
                }]
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': name
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'kms': KEY_ARN,
                    'tier': 'Advanced',
                    'tags': {
                        'Test': 'New'
                    }
                }
            )

            assert entry.changes() == {
                'Exists': True,
                'ChangesList': [{
                    'HasChanges': True,
                    'Key': 'Value',
                    'OldValue': 'AWSData',
                    'Replaceable': True,
                    'Value': 'PlainTextData'
                }, {
                    'HasChanges': True,
                    'Key': 'Description',
                    'OldValue': 'ssm description CHANGED',
                    'Replaceable': True,
                    'Value': 'ssm description',
                }, {
                    'HasChanges': True,
                    'Key': 'KeyId',
                    'OldValue': KEY_ARN1,
                    'Replaceable': True,
                    'Value': KEY_ARN
                }, {
                    'HasChanges': True,
                    'Key': 'Type',
                    'OldValue': 'String',
                    'Replaceable': False,
                    'Value': 'SecureString'
                }, {
                    'HasChanges': True,
                    'Key': 'Tier',
                    'OldValue': 'Standard',
                    'Replaceable': True,
                    'Value': 'Advanced'
                }, {
                    'HasChanges': True,
                    'Key': 'Tags',
                    'OldValue': [{'Key': 'Test', 'Value': 'Old'}],
                    'Replaceable': True,
                    'Value': [{'Key': 'Test', 'Value': 'New'}],
                }]
            }


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_calculate_changes_with_tier_replaceable_false(mock_decrypt):
    """
        Should calculate the changes between AWS resource and local resource

        Scenario:
            - Parameter exists
            - Value changed
            - Description changed
            - Type changed
            - Tier changed and not replaceable
            - Kms changed
            - Tags changed
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': name,
                    'Description': f'{description} CHANGED',
                    'Type': 'String',
                    'KeyId': KEY_ARN1,
                    'Tier': 'Advanced'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': [name]
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'AWSData'
                }
            }, {
                'Name': name,
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': [{
                    'Key': 'Test',
                    'Value': 'Old'
                }]
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': name
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'kms': KEY_ARN,
                    'tier': 'Standard',
                    'tags': {
                        'Test': 'New'
                    }
                }
            )

            assert entry.changes() == {
                'Exists': True,
                'ChangesList': [{
                    'HasChanges': True,
                    'Key': 'Value',
                    'OldValue': 'AWSData',
                    'Replaceable': True,
                    'Value': 'PlainTextData'
                }, {
                    'HasChanges': True,
                    'Key': 'Description',
                    'OldValue': 'ssm description CHANGED',
                    'Replaceable': True,
                    'Value': 'ssm description',
                }, {
                    'HasChanges': True,
                    'Key': 'KeyId',
                    'OldValue': KEY_ARN1,
                    'Replaceable': True,
                    'Value': KEY_ARN
                }, {
                    'HasChanges': True,
                    'Key': 'Type',
                    'OldValue': 'String',
                    'Replaceable': False,
                    'Value': 'SecureString'
                }, {
                    'HasChanges': True,
                    'Key': 'Tier',
                    'OldValue': 'Advanced',
                    'Replaceable': False,
                    'Value': 'Standard'
                }, {
                    'HasChanges': True,
                    'Key': 'Tags',
                    'OldValue': [{'Key': 'Test', 'Value': 'Old'}],
                    'Replaceable': True,
                    'Value': [{'Key': 'Test', 'Value': 'New'}],
                }]
            }


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_calculate_changes_without_changes(mock_decrypt):
    """
        Should calculate the changes between AWS resource and local resource

        Scenario:
            - Parameter exists
            - Value not changed
            - Description not changed
            - Type not changed
            - Tier not changed
            - Kms not changed
            - Tags not changed
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': name,
                    'Description': description,
                    'Type': 'SecureString',
                    'KeyId': KEY_ARN,
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': [name]
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': name,
                'WithDecryption': True
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': [{
                    'Key': 'Test',
                    'Value': 'New'
                }]
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': name
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'kms': KEY_ARN,
                    'tags': {
                        'Test': 'New'
                    }
                }
            )

            assert entry.changes() == {
                'Exists': True,
                'ChangesList': []
            }


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_create_advanced_tier(mock_decrypt):
    """
        Should create the SSM parameter in the AWS environment
    """
    client = boto3.client('ssm')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'ssm-param'
            description = 'ssm description'
            ssm_type = 'SecureString'

            mock_client.return_value = client
            stubber.add_response('put_parameter', {}, {
                'Name': name,
                'Description': description,
                'Type': ssm_type,
                'Value': 'PlainTextData',
                'Tier': 'Advanced',
                'KeyId': KEY_ARN,
                'Tags': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SSMParameterEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'type': ssm_type,
                    'tier': 'Advanced',
                    'kms': KEY_ARN
                }
            )

            entry.create()
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)
