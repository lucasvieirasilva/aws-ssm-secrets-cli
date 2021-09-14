import pytest
from aws_secrets.miscellaneous import utils


@pytest.mark.parametrize("value,size,expected", [
    ('#', 5, "#####"),
    ('=', 10, "=========="),
    ('=', 1, "=")
])
def test_repeat_to_length(value, size, expected):
    """
        Should generate the string correctly
    """
    assert utils.repeat_to_length(value, size) == expected
