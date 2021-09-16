from unittest.mock import patch

import boto3
from aws_secrets.cli.cli import cli
from botocore.stub import Stubber

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
SECRET_ARN = 'arn:aws:secretsmanager:us-west-2:111122223333:secret:aes256-7g8H9i'


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('subprocess.run')
def test_deploy_parameters(
    mock_run,
    mock_decrypt,
    mock_cli_runner
):
    """
        Should deploy the changes to the AWS environment
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            _ssm_parameters_stubs(stubber)

            with mock_cli_runner.isolated_filesystem():
                with open(config_file, 'w') as config:
                    with open(config_file, 'w') as config:
                        config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
- name: ssm2
  type: String
  value: PlainText2
- name: ssm3
  type: String
  value: !cmd 'value'
- name: ssm4
  type: SecureString
  value: !cmd 'value'
secrets_file: ./config.secrets.yaml
""")
                with open(secrets_file, 'w') as secrets:
                    secrets.write("""parameters:
- name: ssm1
  value: SecretData
""")

                result = mock_cli_runner.invoke(cli, [
                    '--loglevel', 'DEBUG',
                    'deploy',
                    '--env-file', config_file
                ])

                assert result.exit_code == 0


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('subprocess.run')
def test_deploy_only_parameters_flag(
    mock_run,
    mock_decrypt,
    mock_cli_runner
):
    """
        Should deploy the changes to the AWS environment with --only-parameters flag
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            _ssm_parameters_stubs(stubber)

            with mock_cli_runner.isolated_filesystem():
                with open(config_file, 'w') as config:
                    with open(config_file, 'w') as config:
                        config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
- name: ssm2
  type: String
  value: PlainText2
- name: ssm3
  type: String
  value: !cmd 'value'
- name: ssm4
  type: SecureString
  value: !cmd 'value'
secrets:
- name: secret1
secrets_file: ./config.secrets.yaml
""")
                with open(secrets_file, 'w') as secrets:
                    secrets.write("""parameters:
- name: ssm1
  value: SecretData
secrets:
- name: secret1
  value: SecretData
""")

                result = mock_cli_runner.invoke(cli, [
                    '--loglevel', 'DEBUG',
                    'deploy',
                    '--env-file', config_file,
                    '--only-parameters'
                ])

                assert result.exit_code == 0


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('subprocess.run')
def test_deploy_secrets(
    mock_run,
    mock_decrypt,
    mock_cli_runner
):
    """
        Should deploy the changes to the AWS environment
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('secretsmanager')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            _secrets_stubs(stubber)

            with mock_cli_runner.isolated_filesystem():
                with open('hello.txt', 'w') as f:
                    f.write("Hello")

                with open(config_file, 'w') as config:
                    with open(config_file, 'w') as config:
                        config.write(f"""kms:
  arn: {KEY_ARN}
secrets:
- name: secret1
- name: secret2
  value: !cmd 'value'
- name: secret3
  value: !file 'hello.txt'
secrets_file: ./config.secrets.yaml
""")
                with open(secrets_file, 'w') as secrets:
                    secrets.write("""secrets:
- name: secret1
  value: SecretData
""")

                result = mock_cli_runner.invoke(cli, [
                    '--loglevel', 'DEBUG',
                    'deploy',
                    '--env-file', config_file
                ])

                assert result.exit_code == 0


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('subprocess.run')
def test_deploy_secrets_only_secrets_flag(
    mock_run,
    mock_decrypt,
    mock_cli_runner
):
    """
        Should deploy the changes to the AWS environment with `--only-secrets` flag
    """
    mock_run.return_value.stdout = 'myvalue'
    mock_decrypt.return_value = b'PlainTextData'
    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('secretsmanager')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            _secrets_stubs(stubber)

            with mock_cli_runner.isolated_filesystem():
                with open('hello.txt', 'w') as f:
                    f.write("Hello")

                with open(config_file, 'w') as config:
                    with open(config_file, 'w') as config:
                        config.write(f"""kms:
  arn: {KEY_ARN}
parameters:
- name: ssm1
  type: SecureString
secrets:
- name: secret1
- name: secret2
  value: !cmd 'value'
- name: secret3
  value: !file 'hello.txt'
secrets_file: ./config.secrets.yaml
""")
                with open(secrets_file, 'w') as secrets:
                    secrets.write("""secrets:
- name: secret1
  value: SecretData
parameters:
- name: ssm1
  value: SecretData
""")

                result = mock_cli_runner.invoke(cli, [
                    '--loglevel', 'DEBUG',
                    'deploy',
                    '--env-file', config_file,
                    '--only-secrets'
                ])

                assert result.exit_code == 0


def _secrets_stubs(stubber):
    stubber.add_response('list_secrets', {
        'SecretList': []
    }, {
        'Filters': [
            {
                'Key': 'name',
                'Values': ['secret1']
            }
        ]
    })
    stubber.add_response('create_secret', {}, {
        'Name': 'secret1',
        'Description': '',
        'SecretString': 'PlainTextData',
        'Tags': []
    })
    stubber.add_response('list_secrets', {
        'SecretList': [{
            'ARN': SECRET_ARN,
            'Name': 'secret2',
            'Description': '',
            'Tags': []
        }]
    }, {
        'Filters': [
            {
                'Key': 'name',
                'Values': ['secret2']
            }
        ]
    })
    stubber.add_response('get_secret_value', {
        'SecretString': 'PlainTextData'
    }, {
        'SecretId': 'secret2'
    })
    stubber.add_response('update_secret', {}, {
        'SecretId': 'secret2',
        'Description': '',
        'SecretString': 'myvalue'
    })
    stubber.add_response('untag_resource', {}, {
        'SecretId': 'secret2',
        'TagKeys': []
    })
    stubber.add_response('list_secrets', {
        'SecretList': []
    }, {
        'Filters': [
            {
                'Key': 'name',
                'Values': ['secret3']
            }
        ]
    })
    stubber.add_response('create_secret', {}, {
        'Name': 'secret3',
        'Description': '',
        'SecretString': 'Hello',
        'Tags': []
    })


def _ssm_parameters_stubs(stubber):
    stubber.add_response('describe_parameters', {
        'Parameters': []
    }, {
        'ParameterFilters': [
            {
                'Key': 'Name',
                'Option': 'Equals',
                'Values': ['ssm1']
            }
        ]
    })
    stubber.add_response('put_parameter', {}, {
        'Name': 'ssm1',
        'Description': '',
        'Type': 'SecureString',
        'Value': 'PlainTextData',
        'Tier': 'Standard',
        'Tags': []
    })
    stubber.add_response('describe_parameters', {
        'Parameters': [{
            'Name': 'ssm2',
            'Description': '',
            'Type': 'String',
            'Tier': 'Standard'
        }]
    }, {
        'ParameterFilters': [
            {
                'Key': 'Name',
                'Option': 'Equals',
                'Values': ['ssm2']
            }
        ]
    })
    stubber.add_response('get_parameter', {
        'Parameter': {
            'Value': 'PlainTextData'
        }
    }, {
        'Name': 'ssm2',
        'WithDecryption': False
    })
    stubber.add_response('list_tags_for_resource', {
        'TagList': []
    }, {
        'ResourceType': 'Parameter',
        'ResourceId': 'ssm2'
    })
    stubber.add_response('put_parameter', {}, {
        'Name': 'ssm2',
        'Description': '',
        'Type': 'String',
        'Value': 'PlainText2',
        'Tier': 'Standard',
        'Overwrite': True,
    })
    stubber.add_response('remove_tags_from_resource', {}, {
        'ResourceType': 'Parameter',
        'ResourceId': 'ssm2',
        'TagKeys': []
    })
    stubber.add_response('describe_parameters', {
        'Parameters': []
    }, {
        'ParameterFilters': [
            {
                'Key': 'Name',
                'Option': 'Equals',
                'Values': ['ssm3']
            }
        ]
    })
    stubber.add_response('put_parameter', {}, {
        'Name': 'ssm3',
        'Description': '',
        'Type': 'String',
        'Value': 'myvalue',
        'Tier': 'Standard',
        'Tags': []
    })
    stubber.add_response('describe_parameters', {
        'Parameters': [{
            'Name': 'ssm4',
            'Description': '',
            'Type': 'SecureString',
            'Tier': 'Standard'
        }]
    }, {
        'ParameterFilters': [
            {
                'Key': 'Name',
                'Option': 'Equals',
                'Values': ['ssm4']
            }
        ]
    })
    stubber.add_response('get_parameter', {
        'Parameter': {
            'Value': 'PlainTextData2'
        }
    }, {
        'Name': 'ssm4',
        'WithDecryption': True
    })
    stubber.add_response('list_tags_for_resource', {
        'TagList': []
    }, {
        'ResourceType': 'Parameter',
        'ResourceId': 'ssm4'
    })
    stubber.add_response('put_parameter', {}, {
        'Name': 'ssm4',
        'Description': '',
        'Type': 'SecureString',
        'Value': 'myvalue',
        'Tier': 'Standard',
        'Overwrite': True
    })
    stubber.add_response('remove_tags_from_resource', {}, {
        'ResourceType': 'Parameter',
        'ResourceId': 'ssm4',
        'TagKeys': []
    })
