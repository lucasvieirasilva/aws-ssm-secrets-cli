from aws_secrets.helpers.logging import setup_logging
from aws_secrets import __name__ as module_name


def test_logging_debug(capsys):
    """
        Should output the debug logs
    """

    logger = setup_logging(module_name, 'DEBUG')

    logger.debug('DEBUG')

    captured = capsys.readouterr()

    assert "DEBUG" in captured.err


def test_logging_info(capsys):
    """
        Should output the debug logs
    """

    logger = setup_logging(module_name, 'INFO')

    logger.debug('DEBUG')
    logger.info('INFO')

    captured = capsys.readouterr()

    assert "INFO" in captured.err
    assert "DEBUG" not in captured.err


def test_logging_warning(capsys):
    """
        Should output the debug logs
    """

    logger = setup_logging(module_name, 'WARNING')

    logger.debug('DEBUG')
    logger.info('INFO')
    logger.warn('WARN')

    captured = capsys.readouterr()

    assert "WARN" in captured.err
    assert "INFO" not in captured.err
    assert "DEBUG" not in captured.err
