from unittest.mock import patch

import boto3
from botocore.stub import Stubber

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.config.providers.secretsmanager.entry import \
    SecretManagerEntry
from aws_secrets.config.providers.secretsmanager.provider import \
    SecretsManagerProvider
from aws_secrets.miscellaneous import session
from aws_secrets.representers.literal import Literal

KEY_ARN = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
SECRET_ARN = "arn:aws:secretsmanager:us-west-2:111122223333:secret:aes256-7g8H9i"


def test_secretsmanager_provider_instance(boto_fs):
    """
    Should create the SecretsManager Provider object
    """

    config_file = "config.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert len(provider.entries) == 0


@patch("aws_secrets.miscellaneous.kms.decrypt")
def test_secretsmanager_provider_decrypt(mock_decrypt, boto_fs):
    """
    Should decrypt all the entries in the provider
    """

    mock_decrypt.return_value = b"PlainTextData"

    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
""",
    )

    boto_fs.create_file(
        secrets_file,
        contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    provider.decrypt()

    assert provider._get_data_entries() == [
        {"name": "secret1", "value": "PlainTextData"}
    ]


@patch("aws_secrets.miscellaneous.kms.decrypt")
def test_secretsmanager_provider_decrypt_multiline(mock_decrypt, boto_fs):
    """
    Should decrypt all the entries in the provider

    Scenario:
        - multiline value
    """

    mock_decrypt.return_value = b"PlainTextData\nLine1\nLine2"

    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
""",
    )

    boto_fs.create_file(
        secrets_file,
        contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    provider.decrypt()

    assert provider._get_data_entries() == [
        {"name": "secret1", "value": Literal("PlainTextData\nLine1\nLine2")}
    ]


def test_secretsmanager_provider_find_parameter(boto_fs):
    """
    Should find the specific entry in the provider
    """

    config_file = "config.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
      value: 'ABC'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert isinstance(provider.find("secret1"), SecretManagerEntry)


def test_secretsmanager_provider_not_find_parameter(boto_fs):
    """
    Should not find the specific entry in the provider
    """

    config_file = "config.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
      value: 'ABC'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert provider.find("secret2") is None


def test_secretsmanager_provider_get_sensible_entries(boto_fs):
    """
    Should not find the specific entry in the provider
    """

    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
""",
    )

    boto_fs.create_file(
        secrets_file,
        contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert provider.get_sensible_entries() == [{"name": "secret1"}]


@patch("aws_secrets.miscellaneous.kms.encrypt")
def test_secretsmanager_provider_encrypt(mock_encrypt, boto_fs):
    """
    Should encrypt all the entries in the provider
    """

    mock_encrypt.return_value = b"SecretData"

    config_file = "config.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
      value: 'PlainTextData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert provider.encrypt() == [{"name": "secret1", "value": "SecretData"}]


def test_secretsmanager_provider_add(boto_fs):
    """
    Should add a new entry to the provider
    """

    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
""",
    )

    boto_fs.create_file(
        secrets_file,
        contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    assert isinstance(
        provider.add({"name": "secret2", "value": "PlainTextData2"}), SecretManagerEntry
    )

    assert provider._get_data_entries() == [
        {"name": "secret1"},
        {"name": "secret2", "value": "PlainTextData2"},
    ]


def test_secretsmanager_provider_update(boto_fs):
    """
    Should update an existing entry
    """

    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"
    session.aws_profile = None
    session.aws_region = "us-east-1"

    boto_fs.create_file(
        config_file,
        contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
    - name: 'secret2'
""",
    )

    boto_fs.create_file(
        secrets_file,
        contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
    - name: 'secret2'
      value: 'SecretData'
""",
    )

    config = ConfigReader(config_file)
    provider = SecretsManagerProvider(config)

    provider.update(
        {"name": "secret1", "value": "PlainTextData", "description": "Desc"}
    )

    assert provider._get_data_entries() == [
        {"name": "secret1", "value": "PlainTextData", "description": "Desc"},
        {"name": "secret2"},
    ]


@patch("aws_secrets.miscellaneous.kms.decrypt")
def test_secretsmanager_provider_deploy_dry_run(mock_decrypt, boto_fs, capsys):
    """
    Should deploy the AWS Secrets Manager changes
    """

    mock_decrypt.return_value = b"PlainTextData"
    client = boto3.client("secretsmanager")

    with patch.object(boto3.Session, "client") as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response(
                "list_secrets",
                {"SecretList": []},
                {"Filters": [{"Key": "name", "Values": ["secret1"]}]},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret2",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret2"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData"},
                {"SecretId": "secret2"},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret3",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret3"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData2"},
                {"SecretId": "secret3"},
            )

            config_file = "config.yaml"
            secrets_file = "config.secrets.yaml"
            session.aws_profile = None
            session.aws_region = "us-east-1"

            boto_fs.create_file(
                config_file,
                contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
    - name: 'secret2'
    - name: 'secret3'
        """,
            )

            boto_fs.create_file(
                secrets_file,
                contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
    - name: 'secret2'
      value: 'SecretData'
    - name: 'secret3'
      value: 'SecretData'
        """,
            )

            config = ConfigReader(config_file)
            provider = SecretsManagerProvider(config)

            provider.deploy(None, True, False, True)

            captured = capsys.readouterr()

            assert "Secret: [secret1]\n--> New Secret\n" in captured.out
            assert (
                "Secret: [secret3]\n--> Changes:\n   -->"
                + " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n"
                in captured.out
            )


@patch("aws_secrets.miscellaneous.kms.decrypt")
def test_secretsmanager_provider_deploy_dry_run_no_diff(mock_decrypt, boto_fs, capsys):
    """
    Should deploy the AWS Secrets Manager changes
    """

    mock_decrypt.return_value = b"PlainTextData"
    client = boto3.client("secretsmanager")

    with patch.object(boto3.Session, "client") as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response(
                "list_secrets",
                {"SecretList": []},
                {"Filters": [{"Key": "name", "Values": ["secret1"]}]},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret2",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret2"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData"},
                {"SecretId": "secret2"},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret3",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret3"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData2"},
                {"SecretId": "secret3"},
            )

            config_file = "config.yaml"
            secrets_file = "config.secrets.yaml"
            session.aws_profile = None
            session.aws_region = "us-east-1"

            boto_fs.create_file(
                config_file,
                contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
    - name: 'secret2'
    - name: 'secret3'
        """,
            )

            boto_fs.create_file(
                secrets_file,
                contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
    - name: 'secret2'
      value: 'SecretData'
    - name: 'secret3'
      value: 'SecretData'
        """,
            )

            config = ConfigReader(config_file)
            provider = SecretsManagerProvider(config)

            provider.deploy(None, True, False, False)

            captured = capsys.readouterr()

            assert "Secret: [secret1]\n--> New Secret\n" in captured.out
            assert (
                "[secret3]\n--> Secret has changes, "
                + "(use --show-diff to see the changes, not recommended when running in CI/CD)\n"
                in captured.out
            )


@patch("aws_secrets.miscellaneous.kms.decrypt")
@patch("click.confirm")
def test_secretsmanager_provider_deploy_confirm_no(
    mock_confirm, mock_decrypt, boto_fs, capsys
):
    """
    Should deploy the AWS Secrets Manager changes
    """

    mock_decrypt.return_value = b"PlainTextData"
    mock_confirm.return_value = False
    client = boto3.client("secretsmanager")

    with patch.object(boto3.Session, "client") as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response(
                "list_secrets",
                {"SecretList": []},
                {"Filters": [{"Key": "name", "Values": ["secret1"]}]},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret2",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret2"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData"},
                {"SecretId": "secret2"},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret3",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret3"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData2"},
                {"SecretId": "secret3"},
            )

            config_file = "config.yaml"
            secrets_file = "config.secrets.yaml"
            session.aws_profile = None
            session.aws_region = "us-east-1"

            boto_fs.create_file(
                config_file,
                contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
    - name: 'secret2'
    - name: 'secret3'
        """,
            )

            boto_fs.create_file(
                secrets_file,
                contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
    - name: 'secret2'
      value: 'SecretData'
    - name: 'secret3'
      value: 'SecretData'
        """,
            )

            config = ConfigReader(config_file)
            provider = SecretsManagerProvider(config)

            provider.deploy(None, False, True, True)

            captured = capsys.readouterr()

            assert "Secret: [secret1]\n--> New Secret\n" in captured.out
            assert (
                "Secret: [secret3]\n--> Changes:\n   -->"
                + " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n"
                in captured.out
            )


@patch("aws_secrets.miscellaneous.kms.decrypt")
def test_secretsmanager_provider_deploy(mock_decrypt, boto_fs, capsys):
    """
    Should deploy the AWS Secrets Manager changes
    """

    mock_decrypt.return_value = b"PlainTextData"
    client = boto3.client("secretsmanager")

    with patch.object(boto3.Session, "client") as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response(
                "list_secrets",
                {"SecretList": []},
                {"Filters": [{"Key": "name", "Values": ["secret1"]}]},
            )
            stubber.add_response(
                "create_secret",
                {},
                {
                    "Name": "secret1",
                    "Description": "",
                    "SecretString": "PlainTextData",
                    "Tags": [],
                },
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret2",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret2"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData"},
                {"SecretId": "secret2"},
            )
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret3",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret3"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData2"},
                {"SecretId": "secret3"},
            )
            stubber.add_response(
                "update_secret",
                {},
                {
                    "SecretId": "secret3",
                    "Description": "",
                    "SecretString": "PlainTextData",
                },
            )
            stubber.add_response(
                "untag_resource", {}, {"SecretId": "secret3", "TagKeys": []}
            )

            config_file = "config.yaml"
            secrets_file = "config.secrets.yaml"
            session.aws_profile = None
            session.aws_region = "us-east-1"

            boto_fs.create_file(
                config_file,
                contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret1'
    - name: 'secret2'
    - name: 'secret3'
        """,
            )

            boto_fs.create_file(
                secrets_file,
                contents="""
secrets:
    - name: 'secret1'
      value: 'SecretData'
    - name: 'secret2'
      value: 'SecretData'
    - name: 'secret3'
      value: 'SecretData'
        """,
            )

            config = ConfigReader(config_file)
            provider = SecretsManagerProvider(config)

            provider.deploy(None, False, False, True)

            captured = capsys.readouterr()

            assert "Secret: [secret1]\n--> New Secret\n" in captured.out
            assert (
                "Secret: [secret3]\n--> Changes:\n   -->"
                + " Value:\n          Old Value: PlainTextData2\n          New Value: PlainTextData\n"
                in captured.out
            )


@patch("aws_secrets.miscellaneous.kms.decrypt")
@patch("click.confirm")
def test_secretsmanager_provider_deploy_no_changes(
    mock_confirm, mock_decrypt, boto_fs, capsys
):
    """
    Should deploy the AWS Secrets Manager changes
    """

    mock_decrypt.return_value = b"PlainTextData"
    mock_confirm.return_value = False
    client = boto3.client("secretsmanager")

    with patch.object(boto3.Session, "client") as mock_client:
        with Stubber(client) as stubber:
            mock_client.return_value = client
            stubber.add_response(
                "list_secrets",
                {
                    "SecretList": [
                        {
                            "ARN": SECRET_ARN,
                            "Name": "secret2",
                            "Description": "",
                            "Tags": [],
                        }
                    ]
                },
                {"Filters": [{"Key": "name", "Values": ["secret2"]}]},
            )
            stubber.add_response(
                "get_secret_value",
                {"SecretString": "PlainTextData"},
                {"SecretId": "secret2"},
            )

            config_file = "config.yaml"
            secrets_file = "config.secrets.yaml"
            session.aws_profile = None
            session.aws_region = "us-east-1"

            boto_fs.create_file(
                config_file,
                contents=f"""
kms:
    arn: {KEY_ARN}
secrets:
    - name: 'secret2'
        """,
            )

            boto_fs.create_file(
                secrets_file,
                contents="""
secrets:
    - name: 'secret2'
      value: 'SecretData'
        """,
            )

            config = ConfigReader(config_file)
            provider = SecretsManagerProvider(config)

            provider.deploy(None, False, True, True)

            captured = capsys.readouterr()

            assert "no changes required" in captured.out
