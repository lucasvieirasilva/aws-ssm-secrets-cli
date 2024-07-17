from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.representer import SafeRepresenter


class Literal(str):
    """
    YAML Literal string representer
    """


def literal_presenter(representer: SafeRepresenter, data: Literal) -> ScalarNode:
    """
    YAML Literal presenter

    Args:
        representer (`SafeRepresenter`): YAML safe representer
        data (`Literal`): raw value

    Returns:
        `ScalarNode` YAML scalar node
    """
    return representer.represent_scalar("tag:yaml.org,2002:str", data, style="|")
