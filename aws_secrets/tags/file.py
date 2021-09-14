import logging
import os
from pathlib import Path

import click
import yaml
from aws_secrets.helpers.catch_exceptions import CLIError
from yaml.dumper import SafeDumper
from yaml.nodes import ScalarNode


class FileTag(yaml.YAMLObject):
    """
        Custom YAML tag class
        !file tag read the content from a file

        Examples:
            >>> !file /path/file.txt
            value: `'hello'`

        Args:
            value (`str`): file path

        Attributes:
            value (`str`): file path
            logger (`Logger`): logger instance
    """

    yaml_tag = u'!file'

    def __init__(self, value: str):
        self.value = value
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        """
            Resolve the file path and read the content

            Returns:
                `str` file content
        """
        click_ctx = click.get_current_context(silent=True)
        working_dir = os.getcwd()

        if click_ctx:
            config_file = click.get_current_context(silent=True).obj.get('config_file', None)
            if config_file is not None:
                working_dir = os.path.basename(config_file)

        source_file_path = Path(os.path.relpath(self.value, working_dir)).resolve()

        if source_file_path.exists():
            return source_file_path.read_text()
        else:
            raise CLIError(f"File '{source_file_path}' not found")

    @classmethod
    def from_yaml(cls, _, node):
        return FileTag(node.value)

    @classmethod
    def to_yaml(cls, dumper: SafeDumper, data) -> ScalarNode:
        return dumper.represent_scalar(cls.yaml_tag, data.value)
