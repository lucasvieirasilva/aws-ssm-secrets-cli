from io import BytesIO
from unittest.mock import Mock, patch

from aws_secrets.cli.cli import cli

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_view_parameter_cli(
    mock_decrypt,
    mock_cli_runner
):
    """
        Should echo the plain text parameter data
    """
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters:
- name: ssm1
  value: SecretData
""")

        result = mock_cli_runner.invoke(cli, [
            'view-parameter',
            '--env-file', config_file,
            '--name', 'ssm1'
        ])

        assert result.exit_code == 0
        assert result.output == 'PlainTextData\n'


def test_view_parameter_cli_type_string(
    mock_cli_runner
):
    """
        Should echo the plain text parameter data with type string
    """
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
            'view-parameter',
            '--env-file', config_file,
            '--name', 'ssm1'
        ])

        assert result.exit_code == 0
        assert result.output == 'ABC\n'


@patch('subprocess.Popen')
def test_view_parameter_cli_with_resolver(
    mock_popen,
    mock_cli_runner
):
    """
        Should echo the plain text parameter data with resolver
    """
    process_mock = Mock()
    process_mock.stdout = BytesIO(b'myvalue')

    mock_popen.return_value = process_mock

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
  value: !cmd "hello"
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters: []""")

        result = mock_cli_runner.invoke(cli, [
            'view-parameter',
            '--env-file', config_file,
            '--name', 'ssm1'
        ])

        assert result.exit_code == 0
        assert 'myvalue\n' in result.output


@patch('subprocess.Popen')
def test_view_parameter_cli_with_resolver_type_string(
    mock_popen,
    mock_cli_runner
):
    """
        Should echo the plain text parameter data with resolver type string
    """
    process_mock = Mock()
    process_mock.stdout = BytesIO(b'myvalue')

    mock_popen.return_value = process_mock

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, 'w') as config:
            config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: String
  value: !cmd "hello"
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, 'w') as secrets:
            secrets.write("""parameters: []""")

        result = mock_cli_runner.invoke(cli, [
            'view-parameter',
            '--env-file', config_file,
            '--name', 'ssm1'
        ])

        assert result.exit_code == 0
        assert 'myvalue\n' in result.output


@patch('subprocess.Popen')
def test_view_parameter_cli_parameter_not_found(
    mock_popen,
    mock_cli_runner
):
    """
        Should raise an exception when the parameter does not exist
    """
    process_mock = Mock()
    process_mock.stdout = BytesIO(b'myvalue')

    mock_popen.return_value = process_mock

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
            'view-parameter',
            '--env-file', config_file,
            '--name', 'ssm2'
        ])

        assert result.exit_code == 1
        assert 'parameter ssm2 not found' in result.output
