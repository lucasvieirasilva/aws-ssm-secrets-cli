import base64

import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
from boto3.session import Session


def encrypt(
    session: Session,
    plain_text: str,
    key_arn: str
) -> bytes:
    """
        Encrypt the plain text value using AWS Encryption KMS

        Args:
            session (`Session`): boto3 session object
            plain_text (`str`): Plain text value
            key_arn (`str`): KMS Key ARN

        Returns:
            `bytes`: encrypted data
    """
    client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    )
    master_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(
        key_ids=[key_arn],
        botocore_session=session._session
    )
    ciphertext, _ = client.encrypt(source=plain_text, key_provider=master_key_provider)

    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt(
    session: Session,
    encrypted_text: str,
    key_arn: str
) -> str:
    """
        Decrypt the encrypted text using AWS Encryption KMS

        Args:
            session (`Session`): boto3 session object
            encrypted_text (`str`): Encrypted text
            key_arn (`str`): KMS Key ARN

        Returns:
            `str`: plain text
    """
    client = aws_encryption_sdk.EncryptionSDKClient(
        commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
    )
    encrypted_text = base64.b64decode(encrypted_text.encode('utf-8'))
    master_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(
        key_ids=[key_arn],
        botocore_session=session._session
    )
    cycled_plaintext, _ = client.decrypt(source=encrypted_text, key_provider=master_key_provider)

    return cycled_plaintext.decode('utf-8')
