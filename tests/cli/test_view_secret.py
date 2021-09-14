from unittest.mock import patch

from aws_secrets.cli.cli import cli

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_view_secret_cli(
    mock_decrypt,
    mock_cli_runner
):
    """
        Should echo the plain text secret data
    """
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
secrets:
- name: secret1
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""secrets:
- name: secret1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            'view-secret',
            '--env-file', config_file,
            '--name', 'secret1'
        ])

        assert result.exit_code == 0
        assert result.output == 'PlainTextData\n'


@patch('subprocess.run')
def test_view_secret_cli_with_resolver(
    mock_run,
    mock_cli_runner
):
    """
        Should echo the plain text secret data with resolver
    """
    mock_run.return_value.stdout = 'myvalue'

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
secrets:
- name: secret1
  value: !cmd "hello"
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""secrets: []""")

        result = mock_cli_runner.invoke(cli, [
            'view-secret',
            '--env-file', config_file,
            '--name', 'secret1'
        ])

        assert result.exit_code == 0
        assert 'myvalue\n' in result.output


@patch('subprocess.run')
def test_view_secret_cli_not_found(
    mock_run,
    mock_cli_runner
):
    """
        Should raise an exception when the secret does not exist
    """
    mock_run.return_value.stdout = 'myvalue'

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: String
  value: ABC
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters: []""")

        result = mock_cli_runner.invoke(cli, [
            'view-secret',
            '--env-file', config_file,
            '--name', 'secret1'
        ])

        assert result.exit_code == 1
        assert 'secret secret1 not found' in result.output
