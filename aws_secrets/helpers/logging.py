import logging
import warnings


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_logging(module: str, loglevel: str) -> logging.Logger:
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
        module (`str`): python module name
        loglevel (`str`): log level
    Returns:
        `Logger`: logger instance
    """

    if loglevel == 'DEBUG':
        cli_logging_level = logging.DEBUG
        logging.getLogger("botocore").setLevel(logging.INFO)
    else:
        cli_logging_level = loglevel
        # Silence botocore logs
        logging.getLogger("botocore").setLevel(logging.CRITICAL)

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(
        fmt="[%(asctime)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger = logging.getLogger(module)
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(log_handler)
    logger.setLevel(cli_logging_level)
    return logger
