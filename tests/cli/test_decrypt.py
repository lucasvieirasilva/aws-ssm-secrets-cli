from unittest.mock import patch

from aws_secrets.cli.cli import cli

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('subprocess.run')
def test_decrypt_cli(
    mock_run,
    mock_decrypt,
    mock_cli_runner
):
    """
        Should decrypt a config file
    """
    mock_run.return_value.stdout = 'myvalue'

    mock_decrypt.return_value = b'PlainText'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'
    output_file = 'decrypted.yaml'

    original_config = f"""kms:
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

    original_secrets = """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
"""

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(original_config)
        with open(secrets_file, 'w') as secrets:
            secrets.write(original_secrets)

        result = mock_cli_runner.invoke(cli, [
            '--loglevel', "DEBUG",
            'decrypt',
            '--env-file', config_file,
            '--output', output_file
        ])

        assert result.exit_code == 0

        with open(config_file, 'r') as config:
            assert config.read() == original_config

        with open(secrets_file, 'r') as secrets:
            assert secrets.read() == original_secrets

        with open(output_file, 'r') as config:
            assert config.read() == f"""kms:
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
  value: !cmd 'value'
- name: ssm4
  type: SecureString
  value: !cmd 'value'
secrets:
- name: secret1
  value: PlainText
- name: secret2
  value: !cmd 'value'
secrets_file: ./config.secrets.yaml
"""
