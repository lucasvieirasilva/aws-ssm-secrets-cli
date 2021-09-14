import pytest
import yaml
from aws_secrets.tags.file import FileTag
from aws_secrets.helpers.catch_exceptions import CLIError


@pytest.mark.parametrize("file_path,content", [
    ('file.txt', "hello world"),
    ('subdir/file.txt', "hello world2"),
    ('../file.txt', "hello world3"),
])
def test_file_tag(fs, file_path, content):
    """
        Should resolve the file in the same folder
    """
    fs.create_file(file_path, contents=content)

    yaml.SafeLoader.add_constructor('!file', FileTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(FileTag, FileTag.to_yaml)

    data = yaml.safe_load(f"""
key: !file {file_path}
""")

    assert str(data['key']) == content


def test_file_tag_not_found(fs):
    """
        Should resolve the file in the same folder
    """
    yaml.SafeLoader.add_constructor('!file', FileTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(FileTag, FileTag.to_yaml)

    data = yaml.safe_load("""
key: !file not_found.txt
""")

    with pytest.raises(CLIError) as error:
        print(str(data['key']))

    assert str(error.value) == "File '/not_found.txt' not found"


def test_cmd_yaml_tag_dump():
    """
        Should generate the YAML correctly
    """
    yaml.SafeLoader.add_constructor('!file', FileTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(FileTag, FileTag.to_yaml)

    data = yaml.safe_load("""
key: !file hello.txt
""")

    assert yaml.safe_dump(data) == "key: !file 'hello.txt'\n"
