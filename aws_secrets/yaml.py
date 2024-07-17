from ruamel.yaml import YAML

from aws_secrets.representers.literal import Literal, literal_presenter
from aws_secrets.tags.cmd import CmdTag
from aws_secrets.tags.file import FileTag
from aws_secrets.tags.output_stack import OutputStackTag

yaml = YAML()

yaml.indent(mapping=2, sequence=4, offset=2)
yaml.register_class(CmdTag)
yaml.register_class(FileTag)
yaml.register_class(OutputStackTag)
yaml.representer.add_representer(Literal, literal_presenter)
