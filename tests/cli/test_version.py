from aws_secrets.cli.cli import cli
from aws_secrets import __version__


def test_version_cli(
    mock_cli_runner,
):
    """
        Should return the CLI version
    """
    result = mock_cli_runner.invoke(cli, ['version'])

    assert result.exit_code == 0
    assert result.output == f'Version: {__version__}\n'
