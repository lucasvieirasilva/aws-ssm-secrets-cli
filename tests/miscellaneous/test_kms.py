import base64
from unittest import mock

import boto3
from aws_secrets.miscellaneous import kms
from botocore.stub import Stubber

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


def test_kms_encrypt():
    """
        Should encrypt the plain text data
    """
    plain_text = 'abc'
    encrypted_data = b'Secret'
    client = boto3.client('kms')

    with mock.patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            stubber.add_response('encrypt', {
                'CiphertextBlob': encrypted_data
            }, {
                'KeyId': KEY_ARN,
                'Plaintext': bytes(plain_text, 'utf-8'),
            })

            mock_client.return_value = client

            assert kms.encrypt(boto3.Session(), plain_text, KEY_ARN) == base64.b64encode(encrypted_data)


def test_kms_decrypt():
    """
        Should decrypt the encrypted value
    """
    encrypted_data = base64.b64encode(b'Secret')
    decrypted_data = 'PlainText'
    client = boto3.client('kms')

    with mock.patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            stubber.add_response('decrypt', {
                'Plaintext': decrypted_data
            }, {
                'KeyId': KEY_ARN,
                'CiphertextBlob': bytes(base64.b64decode(encrypted_data)),
            })

            mock_client.return_value = client

            assert kms.decrypt(boto3.Session(), encrypted_data, KEY_ARN) == decrypted_data
