from io import StringIO

import pytest

from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.yaml import yaml


@pytest.mark.parametrize(
    "file_path,content",
    [
        ("file.txt", "hello world"),
        ("subdir/file.txt", "hello world2"),
        ("../file.txt", "hello world3"),
    ],
)
def test_file_tag(fs, file_path, content):
    """
    Should resolve the file in the same folder
    """
    fs.create_file(file_path, contents=content)

    data = yaml.load(f"""
key: !file {file_path}
""")

    assert str(data["key"]) == content


def test_file_tag_not_found(fs):
    """
    Should resolve the file in the same folder
    """
    data = yaml.load("""
key: !file not_found.txt
""")

    with pytest.raises(CLIError) as error:
        print(str(data["key"]))

    assert str(error.value) == "File '/not_found.txt' not found"


def test_cmd_yaml_tag_dump():
    """
    Should generate the YAML correctly
    """
    data = yaml.load("""
key: !file hello.txt
""")

    string_stream = StringIO()
    yaml.dump(data, string_stream)

    assert string_stream.getvalue() == "key: !file hello.txt\n"
