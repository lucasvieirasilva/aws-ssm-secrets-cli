import logging
import warnings


def _get_formatter(custom_format=None):
    """
        Get Logger Formatter
        [%(asctime)s] - %(message)s
        Args:
            custom_format: custom format `string`
        Returns:
            logger formatter `logging.Formatter`
    """

    fmt = "[%(asctime)s] - %(message)s"
    if custom_format:
        fmt = custom_format

    return logging.Formatter(
        fmt=fmt,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_logging(module, loglevel):
    """
    Sets up logging.
    By default, the python logging module is configured to push logs to stdout
    as long as their level is at least INFO. The log format is set to
    "[%(asctime)s] - %(name)s - %(message)s" and the date format is set to
    "%Y-%m-%d %H:%M:%S".
    After this function has run, modules should:
    .. code:: python
        import logging
        logging.getLogger(__name__).info("my log message")
    Args:
        module: python module name `string`
        loglevel: log level `string`
    Returns:
        A logger.
    """

    if loglevel == 'DEBUG':
        cli_logging_level = logging.DEBUG
        logging.getLogger("botocore").setLevel(logging.INFO)
    else:
        cli_logging_level = loglevel
        # Silence botocore logs
        logging.getLogger("botocore").setLevel(logging.CRITICAL)

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(_get_formatter())
    logger = logging.getLogger(module)
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(log_handler)
    logger.setLevel(cli_logging_level)
    return logger
