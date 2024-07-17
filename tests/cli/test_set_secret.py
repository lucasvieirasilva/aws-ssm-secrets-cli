from unittest.mock import ANY, patch

from aws_secrets.cli.cli import cli

KEY_ARN = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
KEY_ARN1 = (
    "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab1"
)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_secret.prompt")
def test_set_secret_cli_no_props(mock_prompt, mock_encrypt, mock_cli_runner):
    """
    Should add a new secret
    """
    mock_prompt.side_effect = ["secret3", "Desc", "PlainText"]

    mock_encrypt.return_value = b"SecretData"
    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, "w") as config:
            config.write(f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, "w") as secrets:
            secrets.write("""\
parameters:
  - name: ssm1
    value: SecretData
secrets:
  - name: secret1
    value: SecretData
""")

        result = mock_cli_runner.invoke(
            cli,
            [
                "--loglevel",
                "DEBUG",
                "set-secret",
                "--env-file",
                config_file,
            ],
        )

        assert result.exit_code == 0

        with open(config_file, "r") as config:
            assert (
                config.read()
                == f"""kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
  - name: secret3
    description: Desc
secrets_file: ./config.secrets.yaml
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
  - name: secret3
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_secret.prompt")
def test_set_secret_cli(mock_prompt, mock_encrypt, mock_cli_runner):
    """
    Should add a new secret
    """
    mock_prompt.side_effect = ["Desc", "PlainText"]

    mock_encrypt.return_value = b"SecretData"
    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, "w") as config:
            config.write(f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, "w") as secrets:
            secrets.write("""\
parameters:
  - name: ssm1
    value: SecretData
secrets:
  - name: secret1
    value: SecretData
""")

        result = mock_cli_runner.invoke(
            cli,
            [
                "--loglevel",
                "DEBUG",
                "set-secret",
                "--env-file",
                config_file,
                "--name",
                "secret3",
            ],
        )

        assert result.exit_code == 0

        with open(config_file, "r") as config:
            assert (
                config.read()
                == f"""kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
  - name: secret3
    description: Desc
secrets_file: ./config.secrets.yaml
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
  - name: secret3
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_secret.prompt")
def test_set_secret_cli_with_description(mock_prompt, mock_encrypt, mock_cli_runner):
    """
    Should add a new secret with `--description`
    """
    mock_prompt.side_effect = ["PlainText"]

    mock_encrypt.return_value = b"SecretData"
    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, "w") as config:
            config.write(f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, "w") as secrets:
            secrets.write("""\
parameters:
  - name: ssm1
    value: SecretData
secrets:
  - name: secret1
    value: SecretData
""")

        result = mock_cli_runner.invoke(
            cli,
            [
                "--loglevel",
                "DEBUG",
                "set-secret",
                "--env-file",
                config_file,
                "--name",
                "secret3",
                "--description",
                "Secret 3",
            ],
        )

        assert result.exit_code == 0

        with open(config_file, "r") as config:
            assert (
                config.read()
                == f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
  - name: secret3
    description: Secret 3
secrets_file: ./config.secrets.yaml
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
  - name: secret3
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_secret.prompt")
def test_set_secret_cli_with_custom_kms(mock_prompt, mock_encrypt, mock_cli_runner):
    """
    Should add a new secret with `--kms`
    """
    mock_prompt.side_effect = ["Desc", "PlainText"]

    mock_encrypt.return_value = b"SecretData"
    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, "w") as config:
            config.write(f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, "w") as secrets:
            secrets.write("""\
parameters:
  - name: ssm1
    value: SecretData
secrets:
  - name: secret1
    value: SecretData
""")

        result = mock_cli_runner.invoke(
            cli,
            [
                "--loglevel",
                "DEBUG",
                "set-secret",
                "--env-file",
                config_file,
                "--name",
                "secret3",
                "--kms",
                KEY_ARN1,
            ],
        )

        assert result.exit_code == 0

        with open(config_file, "r") as config:
            assert (
                config.read()
                == f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
  - name: secret2
    value: !cmd value
  - name: secret3
    description: Desc
    kms: {KEY_ARN1}
secrets_file: ./config.secrets.yaml
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
  - name: secret3
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.miscellaneous.kms.decrypt")
@patch("aws_secrets.cli.set_secret.prompt")
def test_set_secret_cli_update_exists_secret(
    mock_prompt, mock_decrypt, mock_encrypt, mock_cli_runner
):
    """
    Should update an existing secret
    """
    mock_prompt.side_effect = ["Desc1", "PlainText"]

    mock_encrypt.return_value = b"ChangedData"
    mock_decrypt.return_value = b"SecretData"
    config_file = "config.yaml"
    secrets_file = "config.secrets.yaml"

    with mock_cli_runner.isolated_filesystem():
        with open(config_file, "w") as config:
            config.write(f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
    description: Desc
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
""")
        with open(secrets_file, "w") as secrets:
            secrets.write("""\
parameters:
  - name: ssm1
    value: SecretData
secrets:
  - name: secret1
    value: SecretData
""")

        result = mock_cli_runner.invoke(
            cli,
            [
                "--loglevel",
                "DEBUG",
                "set-secret",
                "--env-file",
                config_file,
                "--name",
                "secret1",
            ],
        )

        assert result.exit_code == 0

        with open(config_file, "r") as config:
            assert (
                config.read()
                == f"""\
kms:
  arn: {KEY_ARN}
parameters:
  - name: ssm1
    type: SecureString
  - name: ssm2
    type: String
    value: PlainText2
  - name: ssm3
    type: String
    value: !cmd value
  - name: ssm4
    type: SecureString
    value: !cmd value
secrets:
  - name: secret1
    description: Desc1
  - name: secret2
    value: !cmd value
secrets_file: ./config.secrets.yaml
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: ChangedData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)
