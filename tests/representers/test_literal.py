from io import StringIO

from aws_secrets.representers.literal import Literal
from aws_secrets.yaml import yaml


def test_literal_yaml():
    """
    Should resolve YAML literal strings
    """

    string_stream = StringIO()
    yaml.dump({"key": Literal("UNIT TESTS")}, string_stream)

    assert string_stream.getvalue() == "key: |-\n  UNIT TESTS\n"
