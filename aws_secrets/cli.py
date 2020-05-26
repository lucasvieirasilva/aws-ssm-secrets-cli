import argparse
import yaml
import os
import sys
from aws_secrets.resolvers import SetParameterResolver, ViewParameterResolver, DeployResolver, SetSecretResolver, MigrateResolver
from aws_secrets.tags import OutputStackTag, CmdTag
from aws_secrets.miscellaneous import session


def main():
    yaml.SafeLoader.add_constructor('!cf_output', OutputStackTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(
        OutputStackTag, OutputStackTag.to_yaml)
    yaml.SafeLoader.add_constructor('!cmd', CmdTag.from_yaml)
    yaml.SafeDumper.add_multi_representer(CmdTag, CmdTag.to_yaml)

    actions = {
        'set-parameter': SetParameterResolver(),
        'set-secret': SetSecretResolver(),
        'view-parameter': ViewParameterResolver(),
        'deploy': DeployResolver(),
        'migrate': MigrateResolver()
    }

    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    parser.add_argument('action', help='action argument',
                        choices=list(actions.keys()))
    parser.add_argument('-h', '--help', action="store_true", default=False)

    opts, _action_args = parser.parse_known_args()

    if opts.action == 'set-parameter':
        parser.add_argument('-e', '--env-file',
                            help='Environment file', type=str, required=True)
        parser.add_argument(
            '-n', '--name', help='SSM Parameter name', type=str, required=True)
        parser.add_argument(
            '-t', '--type', choices=['String', 'SecureString'], help='SSM Parameter Type', default='SecureString')
        parser.add_argument('--profile', help='AWS Profile', type=str)
        parser.add_argument('--region', help='AWS Region', type=str)

    elif opts.action == 'set-secret':
        parser.add_argument('-e', '--env-file',
                            help='Environment file', type=str, required=True)
        parser.add_argument(
            '-n', '--name', help='Secret name', type=str, required=True)
        parser.add_argument('--profile', help='AWS Profile', type=str)
        parser.add_argument('--region', help='AWS Region', type=str)

    elif opts.action == 'view-parameter':
        parser.add_argument('-e', '--env-file',
                            help='Environment file', type=str, required=True)
        parser.add_argument(
            '-n', '--name', help='SSM Parameter name', type=str, required=True)
        parser.add_argument('--non-decrypt', action='store_true')
        parser.add_argument('--profile', help='AWS Profile', type=str)
        parser.add_argument('--region', help='AWS Region', type=str)

    elif opts.action == 'deploy':
        parser.add_argument('-e', '--env-file',
                            help='Environment file', type=str, required=True)
        parser.add_argument('--profile', help='AWS Profile', type=str)
        parser.add_argument('--region', help='AWS Region', type=str)

    elif opts.action == 'migrate':
        parser.add_argument(
            '-s', '--source', help='Source Environment file', type=str)
        parser.add_argument(
            '-T', '--target', help='Target Environment file', type=str)
        parser.add_argument('--source-profile', help='AWS Profile', type=str)
        parser.add_argument('--source-region', help='AWS Region', type=str)
        parser.add_argument('--target-profile', help='AWS Profile', type=str)
        parser.add_argument('--target-region', help='AWS Region', type=str)

    if opts.help:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    session.aws_profile = args.profile
    session.aws_region = args.region

    actions[args.action].__call__(args)


if __name__ == "__main__":
    main()
