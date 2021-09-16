from unittest.mock import patch

import boto3
from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.config.providers.ssm.entry import SSMParameterEntry
from aws_secrets.config.providers.ssm.provider import SSMProvider
from aws_secrets.miscellaneous import session
from aws_secrets.representers.literal import Literal
from botocore.stub import Stubber

KEY_ARN = 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'


def test_ssm_provider_instance(boto_fs):
    """
        Should create the SSM Provider object
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
""")

    config = ConfigReader(config_file)

    provider = SSMProvider(config)

    assert len(provider.entries) == 0


def test_ssm_provider_decrypt_parameter_not_secure_string(boto_fs):
    """
        Should decrypt all the entries in the provider

        Scenario:
            - SSM parameter is not secure string
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'ABC'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    provider.decrypt()

    assert provider._get_data_entries() == [{
        'name': 'ssm-param',
        'type': 'String',
        'value': 'ABC'
    }]


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_ssm_provider_decrypt_parameter_secure_string(
    mock_decrypt,
    boto_fs
):
    """
        Should decrypt all the entries in the provider

        Scenario:
            - SSM parameter is secure string
    """

    mock_decrypt.return_value = b'PlainTextData'

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'SecureString'
""")

    boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param'
      value: 'SecretData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    provider.decrypt()

    assert provider._get_data_entries() == [{
        'name': 'ssm-param',
        'type': 'SecureString',
        'value': 'PlainTextData'
    }]


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_ssm_provider_decrypt_parameter_secure_string_multiline(
    mock_decrypt,
    boto_fs
):
    """
        Should decrypt all the entries in the provider

        Scenario:
            - SSM parameter is not secure string with multiline value
    """

    mock_decrypt.return_value = b'PlainTextData\nLine1\nLine2'

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'SecureString'
""")

    boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param'
      value: 'SecretData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    provider.decrypt()

    assert provider._get_data_entries() == [{
        'name': 'ssm-param',
        'type': 'SecureString',
        'value': Literal('PlainTextData\nLine1\nLine2')
    }]


def test_ssm_provider_find_parameter(boto_fs):
    """
        Should find the specific entry in the provider
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'ABC'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    assert isinstance(provider.find('ssm-param'), SSMParameterEntry)


def test_ssm_provider_not_find_parameter(boto_fs):
    """
        Should not find the specific entry in the provider
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'ABC'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    assert provider.find('ssm-paramm') is None


def test_ssm_provider_get_sensible_entries(boto_fs):
    """
        Should not find the specific entry in the provider
    """

    config_file = 'config.yaml'
    secrets_file = 'config.secrets.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'ABC'
    - name: 'ssm-param1'
      type: 'SecureString'
""")

    boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param1'
      value: 'SecretData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    assert provider.get_sensible_entries() == [{
        'name': 'ssm-param1',
        'type': 'SecureString'
    }]


@patch('aws_secrets.miscellaneous.kms.encrypt')
def test_ssm_provider_encrypt_parameter_secure_string(
    mock_encrypt,
    boto_fs
):
    """
        Should encrypt all the entries in the provider

        Scenario:
            - SSM parameter is secure string
    """

    mock_encrypt.return_value = b'SecretData'

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'SecureString'
      value: 'PlainTextData'
    - name: 'ssm-param2'
      type: 'String'
      value: 'PlainTextData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    assert provider.encrypt() == [{
        'name': 'ssm-param',
        'value': 'SecretData'
    }]


def test_ssm_provider_add(
    boto_fs
):
    """
        Should add a new entry to the provider
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'PlainTextData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    assert isinstance(provider.add({
        'name': 'ssm-param2',
        'type': 'String',
        'value': 'PlainTextData2'
    }), SSMParameterEntry)

    assert provider._get_data_entries() == [{
        'name': 'ssm-param',
        'type': 'String',
        'value': 'PlainTextData'
    }, {
        'name': 'ssm-param2',
        'type': 'String',
        'value': 'PlainTextData2'
    }]


def test_ssm_provider_update(
    boto_fs
):
    """
        Should update an existing entry
    """

    config_file = 'config.yaml'
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param2'
      type: 'String'
      value: 'PlainTextData'
""")

    config = ConfigReader(config_file)
    provider = SSMProvider(config)

    provider.update({
        'name': 'ssm-param',
        'type': 'String',
        'value': 'PlainTextData',
        'description': 'Desc'
    })

    assert provider._get_data_entries() == [{
        'name': 'ssm-param',
        'type': 'String',
        'value': 'PlainTextData',
        'description': 'Desc'
    }, {
        'name': 'ssm-param2',
        'type': 'String',
        'value': 'PlainTextData'
    }]


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_ssm_provider_deploy_dry_run(
    mock_decrypt,
    boto_fs,
    capsys
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': []
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param']
                    }
                ]
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param2',
                    'Description': '',
                    'Type': 'SecureString',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param2']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData2'
                }
            }, {
                'Name': 'ssm-param2',
                'WithDecryption': True
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param2'
            })

            config_file = 'config.yaml'
            secrets_file = 'config.secrets.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param1'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param2'
      type: 'SecureString'
        """)

            boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param2'
      value: 'SecretData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy('ssm-param*', True, False)

            captured = capsys.readouterr()

            assert "Parameter: [ssm-param]\n--> New Parameter\n" in captured.out
            assert "Parameter: [ssm-param2]\n--> Changes:\n   -->" + \
                " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n" in captured.out


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('click.confirm')
def test_ssm_provider_deploy_confirm_no(
    mock_confirm,
    mock_decrypt,
    boto_fs,
    capsys
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    mock_confirm.return_value = False
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': []
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param']
                    }
                ]
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param2',
                    'Description': '',
                    'Type': 'SecureString',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param2']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData2'
                }
            }, {
                'Name': 'ssm-param2',
                'WithDecryption': True
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param2'
            })

            config_file = 'config.yaml'
            secrets_file = 'config.secrets.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param1'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param2'
      type: 'SecureString'
        """)

            boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param2'
      value: 'SecretData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy('ssm-param*', False, True)

            captured = capsys.readouterr()

            assert "Parameter: [ssm-param]\n--> New Parameter\n" in captured.out
            assert "Parameter: [ssm-param2]\n--> Changes:\n   -->" + \
                " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n" in captured.out


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_ssm_provider_deploy(
    mock_decrypt,
    boto_fs,
    capsys
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': []
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param']
                    }
                ]
            })
            stubber.add_response('put_parameter', {}, {
                'Name': 'ssm-param',
                'Description': '',
                'Type': 'String',
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Tags': []
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param2',
                    'Description': '',
                    'Type': 'SecureString',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param2']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData2'
                }
            }, {
                'Name': 'ssm-param2',
                'WithDecryption': True
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param2'
            })
            stubber.add_response('put_parameter', {}, {
                'Name': 'ssm-param2',
                'Description': '',
                'Type': 'SecureString',
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Overwrite': True
            })
            stubber.add_response('remove_tags_from_resource', {}, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param2',
                'TagKeys': []
            })

            config_file = 'config.yaml'
            secrets_file = 'config.secrets.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param1'
      type: 'String'
      value: 'PlainTextData'
    - name: 'ssm-param2'
      type: 'SecureString'
        """)

            boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param2'
      value: 'SecretData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy('ssm-param*', False, False)

            captured = capsys.readouterr()

            assert "Parameter: [ssm-param]\n--> New Parameter\n" in captured.out
            assert "Parameter: [ssm-param2]\n--> Changes:\n   -->" + \
                " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n" in captured.out


@patch('aws_secrets.miscellaneous.kms.decrypt')
def test_ssm_provider_deploy_no_changes(
    mock_decrypt,
    boto_fs,
    capsys
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })

            config_file = 'config.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param1'
      type: 'String'
      value: 'PlainTextData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy('ssm-param*', False, False)

            captured = capsys.readouterr()

            assert "no changes required" in captured.out


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('click.confirm')
def test_ssm_provider_deploy_non_replaceable_attrs(
    mock_confirm,
    mock_decrypt,
    boto_fs
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    mock_confirm.return_value = True
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })
            stubber.add_response('delete_parameter', {}, {
                'Name': 'ssm-param1'
            })
            stubber.add_response('put_parameter', {}, {
                'Name': 'ssm-param1',
                'Description': '',
                'Type': 'SecureString',
                'Value': 'PlainTextData',
                'Tier': 'Standard',
                'Tags': []
            })

            config_file = 'config.yaml'
            secrets_file = 'config.secrets.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param1'
      type: 'SecureString'
        """)

            boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param1'
      value: 'SecretData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy('ssm-param*', False, False)


@patch('aws_secrets.miscellaneous.kms.decrypt')
@patch('click.confirm')
def test_ssm_provider_deploy_non_replaceable_attrs_confirm_no(
    mock_confirm,
    mock_decrypt,
    boto_fs
):
    """
        Should deploy the SSM parameter changes
    """

    mock_decrypt.return_value = b'PlainTextData'
    mock_confirm.return_value = False
    client = boto3.client('ssm')

    with patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response('describe_parameters', {
                'Parameters': [{
                    'Name': 'ssm-param1',
                    'Description': '',
                    'Type': 'String',
                    'Tier': 'Standard'
                }]
            }, {
                'ParameterFilters': [
                    {
                        'Key': 'Name',
                        'Option': 'Equals',
                        'Values': ['ssm-param1']
                    }
                ]
            })
            stubber.add_response('get_parameter', {
                'Parameter': {
                    'Value': 'PlainTextData'
                }
            }, {
                'Name': 'ssm-param1',
                'WithDecryption': False
            })
            stubber.add_response('list_tags_for_resource', {
                'TagList': []
            }, {
                'ResourceType': 'Parameter',
                'ResourceId': 'ssm-param1'
            })

            config_file = 'config.yaml'
            secrets_file = 'config.secrets.yaml'
            session.aws_profile = None
            session.aws_region = 'us-east-1'

            boto_fs.create_file(config_file, contents=f"""
kms:
    arn: {KEY_ARN}
parameters:
    - name: 'ssm-param1'
      type: 'SecureString'
        """)

            boto_fs.create_file(secrets_file, contents="""
parameters:
    - name: 'ssm-param1'
      value: 'SecretData'
        """)

            config = ConfigReader(config_file)
            provider = SSMProvider(config)

            provider.deploy(None, False, False)
