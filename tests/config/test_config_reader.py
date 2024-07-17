from unittest.mock import patch

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.config.providers.secretsmanager.provider import \
    SecretsManagerProvider
from aws_secrets.config.providers.ssm.provider import SSMProvider
from aws_secrets.miscellaneous import session
from aws_secrets.tags.cmd import CmdTag

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


def test_config_reader_get_providers(boto_fs):
    """
        Should create the Config reader object from the config file
    """
    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
""")

    config = ConfigReader(config_file)

    assert isinstance(config.get_provider('secrets'), SecretsManagerProvider)
    assert isinstance(config.get_provider('parameters'), SSMProvider)


def test_config_reader_secrets_path_prop(boto_fs):
    """
        Should read the secrets path file from the config yaml
    """
    config_file = 'ssm/config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
secrets_file: ./config.secrets.yaml
""")

    config = ConfigReader(config_file)

    assert config.secrets_file_path == '/ssm/config.secrets.yaml'


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_config_reader_decrypt(mock_decrypt, boto_fs):
    """
        Should decrypt all the secrets and parameters
    """

    mock_decrypt.return_value = b'PlainTextData'

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm1'
      type: 'SecureString'
secrets:
    - name: 'secret1'
""")

    boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm1'
      value: 'SecretData'
secrets:
    - name: 'secret1'
      value: 'SecretData'
""")

    config = ConfigReader(config_file)

    config.decrypt()

    assert config.data['parameters'][0]['value'] == 'PlainTextData'
    assert config.data['secrets'][0]['value'] == 'PlainTextData'


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_config_reader_encrypt(mock_encrypt, boto_fs):
    """
        Should encrypt all the secrets and parameters
    """

    mock_encrypt.return_value = b'SecretData'

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm1'
      type: 'SecureString'
      value: 'PlainTextData'
    - name: 'ssm2'
      type: 'SecureString'
      value: !cmd "value"
secrets:
    - name: 'secret1'
      value: 'PlainTextData'
""")

    config = ConfigReader(config_file)

    config.encrypt()

    assert 'value' not in config.data['parameters'][0]
    assert isinstance(config.data['parameters'][1]['value'], CmdTag)
    assert 'value' not in config.data['secrets'][0]
    assert config.secrets_data['parameters'][0]['value'] == 'SecretData'
    assert config.secrets_data['secrets'][0]['value'] == 'SecretData'


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_config_reader_encrypt_and_save(mock_encrypt, boto_fs):
    """
        Should encrypt all the secrets and parameters and save on the disk
    """

    mock_encrypt.return_value = b'SecretData'

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm1'
      type: 'SecureString'
      value: 'PlainTextData'
    - name: 'ssm2'
      type: 'SecureString'
      value: !cmd value
secrets:
    - name: 'secret1'
      value: 'PlainTextData'
""")

    config = ConfigReader(config_file)

    config.encrypt()
    config.save()

    with open(config_file, 'r') as conf_data:
        assert conf_data.read() == f"""kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
secrets_file: ./config.secrets.yaml
"""

    with open('config.secrets.yaml', 'r') as secrets_data:
        assert secrets_data.read() == """\
secrets:
  - name: secret1
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
