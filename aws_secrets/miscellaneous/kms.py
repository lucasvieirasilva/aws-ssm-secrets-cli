import base64

from botocore.session import Session


def encrypt(
    session: Session,
    plain_text: str,
    key_arn: str
) -> bytes:
    """
        Encrypt the plain text value using KMS

        Args:
            session (`Session`): boto3 session object
            plain_text (`str`): Plain text value
            key_arn (`str`): KMS Key ARN

        Returns:
            `bytes`: encrypted data
    """
    client = session.client('kms')
    ciphertext = client.encrypt(
        KeyId=key_arn,
        Plaintext=bytes(plain_text, 'utf-8'),
    )
    return base64.b64encode(ciphertext["CiphertextBlob"])


def decrypt(
    session: Session,
    encrypted_text: str,
    key_arn: str
) -> str:
    """
        Decrypt the encrypted text using KMS

        Args:
            session (`Session`): boto3 session object
            encrypted_text (`str`): Encrypted text
            key_arn (`str`): KMS Key ARN

        Returns:
            `str`: plain text
    """
    client = session.client('kms')
    decoded_value = base64.b64decode(encrypted_text)
    plaintext = client.decrypt(
        KeyId=key_arn,
        CiphertextBlob=bytes(decoded_value)
    )
    return plaintext["Plaintext"]
