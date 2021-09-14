import pytest

from click.testing import CliRunner


@pytest.fixture
def mock_cli_runner():
    return CliRunner()
