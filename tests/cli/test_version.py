from unittest.mock import Mock, patch

import toml
from aws_secrets.cli.cli import cli


@patch('pkg_resources.get_distribution')
def test_version_cli(
    mock_get_distribution,
    mock_cli_runner,
):
    """
        Should return the CLI version
    """
    with open('pyproject.toml', 'r') as pyproject:
        toml_data = toml.loads(pyproject.read())

    version_value = toml_data.get('tool', {}).get('poetry', {}).get('version')

    mock_distribution = Mock()
    mock_distribution.version = version_value
    mock_get_distribution.return_value = mock_distribution

    result = mock_cli_runner.invoke(cli, ['version'])

    assert result.exit_code == 0
    assert result.output == f'Version: {version_value}\n'
