import yaml

from aws_secrets.representers.literal import Literal, literal_presenter
from aws_secrets.tags.cmd import CmdTag
from aws_secrets.tags.output_stack import OutputStackTag
from aws_secrets.tags.file import FileTag

yaml.SafeLoader.add_constructor('!cf_output', OutputStackTag.from_yaml)
yaml.SafeDumper.add_multi_representer(
    OutputStackTag, OutputStackTag.to_yaml)

yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

yaml.SafeLoader.add_constructor('!file', FileTag.from_yaml)
yaml.SafeDumper.add_multi_representer(FileTag, FileTag.to_yaml)

yaml.SafeDumper.add_representer(Literal, literal_presenter)

__version__ = '1.2.0b1'
