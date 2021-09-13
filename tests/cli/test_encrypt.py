from io import BytesIO
from unittest.mock import Mock, patch

from aws_secrets.cli.cli import cli

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


@patch('aws_secrets.miscellaneous.kms.encrypt')
@patch('subprocess.Popen')
def test_encrypt_cli(
    mock_popen,
    mock_encrypt,
    mock_cli_runner
):
    """
        Should encrypt a config file
    """
    process_mock = Mock()
    process_mock.stdout = BytesIO(b'myvalue')

    mock_popen.return_value = process_mock

    mock_encrypt.return_value = b'SecretData'
    config_file = 'config.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: ssm1
      type: SecureString
      value: PlainText
    - name: ssm2
      type: String
      value: PlainText2
    - name: ssm3
      type: String
      value: !cmd "value"
    - name: ssm4
      type: SecureString
      value: !cmd "value"
secrets:
    - name: secret1
      value: PlainText
    - name: secret2
      value: !cmd "value"
""")

        result = mock_cli_runner.invoke(cli, [
            'encrypt',
            '--env-file', config_file
        ])

        assert result.exit_code == 0

        with open(config_file, 'r') as config:
            assert config.read() == f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
- name: ssm2
  type: String
  value: PlainText2
- name: ssm3
  type: String
  value: !cmd 'value'
- name: ssm4
  type: SecureString
  value: !cmd 'value'
secrets:
- name: secret1
- name: secret2
  value: !cmd 'value'
secrets_file: ./config.secrets.yaml
"""

        with open('config.secrets.yaml', 'r') as secrets:
            assert secrets.read() == """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
"""
