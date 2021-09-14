import json
from unittest.mock import patch

import boto3
from aws_secrets.config.providers.secretsmanager.entry import SecretManagerEntry
from aws_secrets.tags.cmd import CmdTag
from botocore.stub import Stubber

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
KEY_ARN1 = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab1'

SECRET_ARN = 'arn:aws:secretsmanager:us-west-2:111122223333:secret:aes256-7g8H9i'


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt(mock_encrypt):
    """
        Should encrypt the raw value
    """

    mock_encrypt.return_value = b'SecretData'

    session = boto3.Session(region_name='us-east-1')

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1',
            'value': 'MyPlainText'
        },
        cipher_text=None
    )

    assert entry.encrypt() == 'SecretData'
    mock_encrypt.assert_called_once_with(session, 'MyPlainText', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt_value_dict(mock_encrypt):
    """
        Should encrypt the raw value
    """

    mock_encrypt.return_value = b'SecretData'

    session = boto3.Session(region_name='us-east-1')

    value = {
        'key': 'MyPlainText'
    }

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1',
            'value': value
        },
        cipher_text=None
    )

    assert entry.encrypt() == 'SecretData'
    mock_encrypt.assert_called_once_with(session, json.dumps(value), KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_encrypt_already_encrypted(mock_encrypt):
    """
        Should not encrypt the raw value when the value is already encrypted
    """

    session = boto3.Session(region_name='us-east-1')

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1'
        },
        cipher_text='SecretData'
    )

    assert entry.encrypt() == 'SecretData'
    mock_encrypt.assert_not_called()


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_decrypt(mock_decrypt):
    """
        Should decrypt the cipher text
    """

    mock_decrypt.return_value = b'PlainTextData'

    session = boto3.Session(region_name='us-east-1')

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1'
        },
        cipher_text='SecretData'
    )

    assert entry.decrypt() == 'PlainTextData'
    mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_decrypt_with_value_data(mock_decrypt):
    """
        Should decrypt the cipher text
    """

    mock_decrypt.return_value = b'PlainTextData'

    session = boto3.Session(region_name='us-east-1')

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1',
            'value': 'SecretData'
        },
        cipher_text=None
    )

    assert entry.decrypt() == 'PlainTextData'
    mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('subprocess.run')
def test_decrypt_with_value_data_not_str(mock_run):
    """
        Should decrypt the cipher text
    """

    session = boto3.Session(region_name='us-east-1')
    mock_run.return_value.stdout = 'myvalue'

    entry = SecretManagerEntry(
        session=session,
        kms_arn=KEY_ARN,
        data={
            'name': 'secret1',
            'value': CmdTag('value')
        },
        cipher_text=None
    )

    assert isinstance(entry.decrypt(), CmdTag)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_create_default_kms(mock_decrypt):
    """
        Should create the secret in the AWS environment
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('create_secret', {}, {
                'Name': name,
                'Description': description,
                'SecretString': 'PlainTextData',
                'Tags': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description
                }
            )

            entry.create()
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_create_custom_kms(mock_decrypt):
    """
        Should create the secret in the AWS environment using a custom Kms key
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('create_secret', {}, {
                'Name': name,
                'Description': description,
                'SecretString': 'PlainTextData',
                'KmsKeyId': KEY_ARN,
                'Tags': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'kms': KEY_ARN
                }
            )

            entry.create()
            assert True
            mock_decrypt.assert_called_once_with(session, 'SecretData', KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_update_default_kms_without_tag_changes(mock_decrypt):
    """
        Should update the secret in the AWS environment without tag changes
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('update_secret', {}, {
                'SecretId': name,
                'Description': description,
                'SecretString': 'PlainTextData'
            })
            stubber.add_response('untag_resource', {}, {
                'SecretId': name,
                'TagKeys': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description
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
        Should update the secret in the AWS environment without tag changes
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('update_secret', {}, {
                'SecretId': name,
                'Description': description,
                'SecretString': 'PlainTextData',
                'KmsKeyId': KEY_ARN
            })
            stubber.add_response('untag_resource', {}, {
                'SecretId': name,
                'TagKeys': []
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
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
        Should update the secret in the AWS environment with tag changes
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('update_secret', {}, {
                'SecretId': name,
                'Description': description,
                'SecretString': 'PlainTextData'
            })
            stubber.add_response('untag_resource', {}, {
                'SecretId': name,
                'TagKeys': ['Test']
            })
            stubber.add_response('tag_resource', {}, {
                'SecretId': name,
                'Tags': [{
                    'Key': 'Test',
                    'Value': 'New'
                }]
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
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
        Should delete the secret in the AWS environment
    """
    client = boto3.client('secretsmanager')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('delete_secret', {}, {
                'SecretId': name,
                'ForceDeleteWithoutRecovery': True
            })

            session = boto3.Session(region_name='us-east-1')

            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description
                }
            )

            entry.delete()
            assert True


def test_calculate_changes_with_parameter_not_exists():
    """
        Should calculate the changes between AWS resource and local resource

        Scenario:
            - secret not exists
    """
    client = boto3.client('secretsmanager')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('list_secrets', {
                'SecretList': []
            }, {
                'Filters': [
                    {
                        'Key': 'name',
                        'Values': [name]
                    }
                ]
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
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
            - Kms changed
            - Tags changed
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('list_secrets', {
                'SecretList': [{
                    'ARN': SECRET_ARN,
                    'Name': name,
                    'Description': f'{description} CHANGED',
                    'KmsKeyId': KEY_ARN1,
                    'Tags': [{
                        'Key': 'Test',
                        'Value': 'Old'
                    }]
                }]
            }, {
                'Filters': [
                    {
                        'Key': 'name',
                        'Values': [name]
                    }
                ]
            })
            stubber.add_response('get_secret_value', {
                'SecretString': 'AWSData'
            }, {
                'SecretId': name
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
                    'kms': KEY_ARN,
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
                    'OldValue': 'secret description CHANGED',
                    'Replaceable': True,
                    'Value': 'secret description',
                }, {
                    'HasChanges': True,
                    'Key': 'KmsKeyId',
                    'OldValue': KEY_ARN1,
                    'Replaceable': True,
                    'Value': KEY_ARN
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
            - secret exists
            - Value not changed
            - Description not changed
            - Type not changed
            - Kms not changed
            - Tags not changed
    """
    client = boto3.client('secretsmanager')
    mock_decrypt.return_value = b'PlainTextData'

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            name = 'secret1'
            description = 'secret description'

            mock_client.return_value = client
            stubber.add_response('list_secrets', {
                'SecretList': [{
                    'ARN': SECRET_ARN,
                    'Name': name,
                    'Description': description,
                    'KmsKeyId': KEY_ARN,
                    'Tags': [{
                        'Key': 'Test',
                        'Value': 'New'
                    }]
                }]
            }, {
                'Filters': [
                    {
                        'Key': 'name',
                        'Values': [name]
                    }
                ]
            })
            stubber.add_response('get_secret_value', {
                'SecretString': 'PlainTextData'
            }, {
                'SecretId': name
            })

            session = boto3.Session(region_name='us-east-1')
            entry = SecretManagerEntry(
                session=session,
                cipher_text='SecretData',
                kms_arn=KEY_ARN,
                data={
                    'name': name,
                    'description': description,
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
