from io import StringIO
from unittest.mock import ANY, patch

import pytest

from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.yaml import yaml


@patch("aws_secrets.miscellaneous.cloudformation.get_output_value")
def test_cf_output_yaml_tag(mock_get_output_value):
    """
    Should resolve the cloudformation stack output value
    """
    output = "myvalue"

    mock_get_output_value.return_value = output

    data = yaml.load("""
key: !cf_output stack.output
""")

    assert str(data["key"]) == output
    mock_get_output_value.assert_called_once_with(ANY, "stack", "output")


@patch("aws_secrets.miscellaneous.cloudformation.get_output_value")
def test_cf_output_yaml_tag_with_region(mock_get_output_value):
    """
    Should resolve the cloudformation stack output value
    """
    output = "myvalue"

    mock_get_output_value.return_value = output

    data = yaml.load("""
key: !cf_output stack.output.region
""")

    assert str(data["key"]) == output
    mock_get_output_value.assert_called_once_with(ANY, "stack", "output")


@patch("aws_secrets.miscellaneous.cloudformation.get_output_value")
def test_cf_output_yaml_tag_invalid_format(mock_get_output_value):
    """
    Should throw an exception when resolve the cloudformation stack output value
    """
    output = "myvalue"

    mock_get_output_value.return_value = output

    data = yaml.load("""
key: !cf_output stack
""")

    with pytest.raises(CLIError) as error:
        print(str(data["key"]))

    assert (
        "value stack is invalid, the correct way to "
        "fill this information is <stack-name>.<output-name> "
        "or <stack-name>.<output-name>.<aws_region>"
    ) == str(error.value)
    mock_get_output_value.assert_not_called()


def test_cf_output_yaml_tag_dump():
    """
    Should generate the correct YAML file using the !cf_output
    """
    data = yaml.load("""
key: !cf_output stack.output
""")

    string_stream = StringIO()
    yaml.dump(data, string_stream)

    assert "key: !cf_output stack.output\n" == string_stream.getvalue()
