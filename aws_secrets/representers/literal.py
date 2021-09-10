from yaml.dumper import SafeDumper
from yaml.nodes import ScalarNode


class Literal(str):
    """
        YAML Literal string representer
    """


def literal_presenter(dumper: SafeDumper, data: str) -> ScalarNode:
    """
        YAML Literal presenter

        Args:
            dumper (`SafeDumper`): YAML safe dumper
            data (`str`): raw value

        Returns:
            `ScalarNode` YAML scalar node
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
