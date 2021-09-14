import pytest
import yaml
from aws_secrets.tags.file import FileTag


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
