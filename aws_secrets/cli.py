import argparse
import yaml
import os
from aws_secrets.resolvers import SetParameterResolver, ViewParameterResolver, DeployResolver, SetSecretResolver, MigrateResolver
from aws_secrets.tags import OutputStackTag, CmdTag
from aws_secrets.miscellaneous import session

def main():
    yaml.SafeLoader.add_constructor('!cf_output', OutputStackTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(OutputStackTag, OutputStackTag.to_yaml)
    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    actions = {
        'set-parameter': SetParameterResolver(),
        'set-secret': SetSecretResolver(),
        'view-parameter': ViewParameterResolver(),
        'deploy': DeployResolver(),
        'migrate': MigrateResolver()
    }

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('action', help='action argument',
                        choices=list(actions.keys()))
    parser.add_argument('-e', '--env-file', type=str)
    parser.add_argument('-p', '--parameter', type=str)
    parser.add_argument('--non-decrypt', action='store_true')
    parser.add_argument('-v', '--value', type=str)
    parser.add_argument(
        '-t', '--type', choices=['String', 'SecureString'], default='SecureString')
    parser.add_argument('-s', '--source', type=str)
    parser.add_argument('-T', '--target', type=str)
    parser.add_argument('--profile', type=str)
    parser.add_argument('--target-profile', type=str)
    parser.add_argument('--region', type=str)
    parser.add_argument('--target-region', type=str)

    args = parser.parse_args()
    session.aws_profile = args.profile
    session.aws_region = args.region

    actions[args.action].__call__(args)

if __name__ == "__main__":
    main()