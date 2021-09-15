import subprocess
from unittest.mock import ANY, patch

import pytest
import yaml
from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.miscellaneous import session
from aws_secrets.tags.cmd import CmdTag


@patch('subprocess.run')
def test_cmd_yaml_tag(mock_run):
    """
        Should execute the command and resolve the value
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    data = yaml.safe_load("""
key: !cmd "echo 'hello'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo 'hello'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


def test_cmd_yaml_tag_dump():
    """
        Should generate the YAML correctly
    """
    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    data = yaml.safe_load("""
key: !cmd "echo 'hello'"
""")

    assert yaml.safe_dump(data) == "key: !cmd 'echo ''hello'''\n"


@patch('subprocess.run')
def test_cmd_yaml_tag_with_session_provider_profile(mock_run):
    """
        Should execute the command and resolve the value that has the session provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_profile = 'fake-profile'

    data = yaml.safe_load("""
key: !cmd "echo '${session:profile}'"
""")

    assert 'myvalue' == str(data['key'])

    session.aws_profile = None
    mock_run.assert_called_once_with("echo 'fake-profile'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_session_provider_region(mock_run):
    """
        Should execute the command and resolve the value that has the session provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = 'us-east-1'

    data = yaml.safe_load("""
key: !cmd "echo '${session:region}'"
""")

    assert 'myvalue' == str(data['key'])

    session.aws_region = None
    mock_run.assert_called_once_with("echo 'us-east-1'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_session_provider_no_region(mock_run):
    """
        Should execute the command and resolve the value that has the session provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${session:region}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo ''".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_session_provider_default_region(mock_run):
    """
        Should execute the command and resolve the value that has the session provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${session:region, us-east-1}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo 'us-east-1'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_session_provider_invalid_prop(mock_run):
    """
        Should throw an exception when the session provider has in invalid property
    """
    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${session:dump}'"
""")

    with pytest.raises(CLIError) as error:
        print(str(data['key']))

    assert 'Property `dump` is not supported, ' + \
        f'provider `session` just supports {str(["profile", "region"])} properties' in str(error.value)

    mock_run.assert_not_called()


@patch('subprocess.run')
def test_cmd_yaml_tag_with_invalid_provider(mock_run):
    """
        Should throw an exception when the provider is invalid
    """
    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${dump:dump}'"
""")

    with pytest.raises(CLIError) as error:
        print(str(data['key']))

    assert 'Provider dump is not supported' in str(error.value)

    mock_run.assert_not_called()


@patch('subprocess.run')
@patch('aws_secrets.miscellaneous.cloudformation.get_output_value')
def test_cmd_yaml_tag_with_cf_provider(mock_get_output_value, mock_run):
    """
        Should execute the command and resolve the value that has the cf provider
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_get_output_value.return_value = 'stack-output'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    data = yaml.safe_load("""
key: !cmd "echo '${cf:stack.output}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo 'stack-output'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')
    mock_get_output_value.assert_called_once_with(ANY, 'stack', 'output')


@patch('subprocess.run')
@patch('aws_secrets.miscellaneous.cloudformation.get_output_value')
def test_cmd_yaml_tag_with_cf_provider_default_value(mock_get_output_value, mock_run):
    """
        Should execute the command and resolve the value that has the cf provider
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_get_output_value.return_value = None

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    data = yaml.safe_load("""
key: !cmd "echo '${cf:stack.output, stack-output}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo 'stack-output'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')
    mock_get_output_value.assert_called_once_with(ANY, 'stack', 'output')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_profile(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_profile = 'fake-profile'

    data = yaml.safe_load("""
key: !cmd "echo '${aws:profile}'"
""")

    assert 'myvalue' == str(data['key'])

    session.aws_profile = None
    mock_run.assert_called_once_with("echo '--profile fake-profile'".split(" "),
                                     stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_profile_default_value(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_profile = None

    data = yaml.safe_load("""
key: !cmd "echo '${aws:profile, fake-profile}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo '--profile fake-profile'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_profile_none(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_profile = None

    data = yaml.safe_load("""
key: !cmd "echo '${aws:profile}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo ''".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_region(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = 'us-east-1'

    data = yaml.safe_load("""
key: !cmd "echo '${aws:region}'"
""")

    assert 'myvalue' == str(data['key'])

    session.aws_region = None
    mock_run.assert_called_once_with("echo '--region us-east-1'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_region_default_value(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${aws:region, us-east-1}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo '--region us-east-1'".split(" "), stdout=subprocess.PIPE, encoding='utf-8')


@patch('subprocess.run')
def test_cmd_yaml_tag_with_aws_provider_region_none(mock_run):
    """
        Should execute the command and resolve the value that has the aws provider
    """
    mock_run.return_value.stdout = 'myvalue'

    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    session.aws_region = None

    data = yaml.safe_load("""
key: !cmd "echo '${aws:region}'"
""")

    assert 'myvalue' == str(data['key'])
    mock_run.assert_called_once_with("echo ''".split(" "), stdout=subprocess.PIPE, encoding='utf-8')
