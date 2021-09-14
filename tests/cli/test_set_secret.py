from unittest.mock import ANY, patch

from aws_secrets.cli.cli import cli

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
KEY_ARN1 = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab1'

input_captured = False
input_value = "PlainText"


def _mock_input():
    global input_captured

    if input_captured is False:
        input_captured = True
        return input_value
    else:
        raise EOFError('')


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_set_secret_cli(
    mock_encrypt,
    mock_cli_runner,
    monkeypatch
):
    """
        Should add a new secret
    """
    global input_captured
    input_captured = False
    monkeypatch.setattr('builtins.input', _mock_input)

    mock_encrypt.return_value = b'SecretData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
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
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            '--loglevel', "DEBUG",
            'set-secret',
            '--env-file', config_file,
            '--name', 'secret3'
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
- name: secret3
secrets_file: ./config.secrets.yaml
"""

        with open(secrets_file, 'r') as secrets:
            assert secrets.read() == """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
- name: secret3
  value: SecretData
"""
        mock_encrypt.assert_called_once_with(ANY, input_value, KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_set_secret_cli_with_description(
    mock_encrypt,
    mock_cli_runner,
    monkeypatch
):
    """
        Should add a new secret with `--description`
    """
    global input_captured
    input_captured = False
    monkeypatch.setattr('builtins.input', _mock_input)

    mock_encrypt.return_value = b'SecretData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
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
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            '--loglevel', "DEBUG",
            'set-secret',
            '--env-file', config_file,
            '--name', 'secret3',
            '--description', 'Secret 3'
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
- description: Secret 3
  name: secret3
secrets_file: ./config.secrets.yaml
"""

        with open(secrets_file, 'r') as secrets:
            assert secrets.read() == """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
- name: secret3
  value: SecretData
"""
        mock_encrypt.assert_called_once_with(ANY, input_value, KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_set_secret_cli_with_custom_kms(
    mock_encrypt,
    mock_cli_runner,
    monkeypatch
):
    """
        Should add a new secret with `--kms`
    """
    global input_captured
    input_captured = False
    monkeypatch.setattr('builtins.input', _mock_input)

    mock_encrypt.return_value = b'SecretData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
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
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            '--loglevel', "DEBUG",
            'set-secret',
            '--env-file', config_file,
            '--name', 'secret3',
            '--kms', KEY_ARN1
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
- kms: {KEY_ARN1}
  name: secret3
secrets_file: ./config.secrets.yaml
"""

        with open(secrets_file, 'r') as secrets:
            assert secrets.read() == """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
- name: secret3
  value: SecretData
"""
        mock_encrypt.assert_called_once_with(ANY, input_value, KEY_ARN)


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_set_secret_cli_update_exists_secret(
    mock_encrypt,
    mock_cli_runner,
    monkeypatch
):
    """
        Should update an existing secret
    """
    global input_captured
    input_captured = False
    monkeypatch.setattr('builtins.input', _mock_input)

    mock_encrypt.return_value = b'ChangedData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
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
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            '--loglevel', "DEBUG",
            'set-secret',
            '--env-file', config_file,
            '--name', 'secret1'
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

        with open(secrets_file, 'r') as secrets:
            assert secrets.read() == """parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: ChangedData
"""
        mock_encrypt.assert_called_once_with(ANY, input_value, KEY_ARN)
