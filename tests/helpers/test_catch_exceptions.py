import pytest
from aws_secrets.helpers.catch_exceptions import catch_exceptions, CLIError


def test_catch_exceptions(caplog):
    """
        Should handle the exception, log the error and exit with code 1
    """
    @catch_exceptions
    def some_stuff():
        raise CLIError('unit tests')

    with pytest.raises((CLIError, SystemExit)) as sys_exit:
        some_stuff()

    assert sys_exit.type == SystemExit
    assert sys_exit.value.code == 1
    assert 'unit tests' in caplog.text


def test_catch_exceptions_no_exception(caplog):
    """
        Should continue the function normally
    """
    @catch_exceptions
    def some_stuff():
        return 'success'

    result = some_stuff()

    assert result == 'success'
