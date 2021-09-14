
import yaml
from aws_secrets.representers.literal import Literal, literal_presenter


def test_literal_yaml():
    """
        Should resolve YAML literal strings
    """

    yaml.SafeDumper.add_representer(Literal, literal_presenter)

    data = yaml.safe_dump({
        'key': Literal('UNIT TESTS')
    })

    assert data == 'key: |-\n  UNIT TESTS\n'
