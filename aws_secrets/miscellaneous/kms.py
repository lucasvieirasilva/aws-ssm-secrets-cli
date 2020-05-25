import base64


def encrypt(session, secret, key_arn):
    client = session.client('kms')
    ciphertext = client.encrypt(
        KeyId=key_arn,
        Plaintext=bytes(secret, 'utf-8'),
    )
    return base64.b64encode(ciphertext["CiphertextBlob"])


def decrypt(session, secret, key_arn):
    client = session.client('kms')
    decoded_value = base64.b64decode(secret)
    plaintext = client.decrypt(
        KeyId=key_arn,
        CiphertextBlob=bytes(decoded_value)
    )
    return plaintext["Plaintext"]
