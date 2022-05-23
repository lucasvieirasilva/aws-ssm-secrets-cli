import base64
from unittest.mock import patch

import boto3

from aws_secrets.miscellaneous import crypto

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


@patch('aws_encryption_sdk.StrictAwsKmsMasterKeyProvider')
@patch('aws_encryption_sdk.EncryptionSDKClient')
def test_encrypt(mock_master_key, mock_client):
    """Should test encryption operation using AWS encryption SDK."""
    session = boto3.Session(region_name='us-east-1')
    encrypted_data = b'EncryptedData'
    mock_client.encrypt.return_value = (encrypted_data, {})
    mock_master_key.return_value = mock_client
    assert crypto.encrypt(session, 'My Text', KEY_ARN) == base64.b64encode(encrypted_data).decode('utf-8')


@patch('aws_encryption_sdk.StrictAwsKmsMasterKeyProvider')
@patch('aws_encryption_sdk.EncryptionSDKClient')
def test_decrypt(mock_master_key, mock_client):
    """Should test decrypt operation using AWS encryption SDK."""
    session = boto3.Session(region_name='us-east-1')
    encrypted_data = base64.b64encode(b'EncryptedData').decode('utf-8')
    mock_client.decrypt.return_value = (b'My Text', {})
    mock_master_key.return_value = mock_client
    assert crypto.decrypt(session, encrypted_data, KEY_ARN) == 'My Text'
