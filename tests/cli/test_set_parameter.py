from unittest.mock import ANY, patch

from aws_secrets.cli.cli import cli

KEY_ARN = "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
KEY_ARN1 = (
    "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab1"
)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_no_props(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should add a new SSM parameter
    """
    mock_prompt.side_effect = ["ssm5", "Desc", "PlainText"]

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
                "set-parameter",
                "--env-file",
                config_file,
                "--type",
                "SecureString",
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
  - name: ssm5
    description: Desc
    type: SecureString
secrets:
  - name: secret1
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
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
  - name: ssm5
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should add a new SSM parameter
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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm5",
                "--type",
                "SecureString",
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
  - name: ssm5
    description: Desc
    type: SecureString
secrets:
  - name: secret1
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
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
  - name: ssm5
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_type_string(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should add a new SSM parameter with type String
    """
    mock_prompt.side_effect = ["Desc", "PlainText"]

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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm5",
                "--type",
                "String",
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
  - name: ssm5
    description: Desc
    type: String
    value: PlainText
secrets:
  - name: secret1
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
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_not_called()


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_with_description(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should add a new SSM parameter with `--description`
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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm5",
                "--description",
                "SSM 5",
                "--type",
                "SecureString",
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
  - name: ssm5
    description: SSM 5
    type: SecureString
secrets:
  - name: secret1
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
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
  - name: ssm5
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_with_custom_kms(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should add a new SSM parameter with `--kms`
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
            secrets.write("""
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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm5",
                "--kms",
                KEY_ARN1,
                "--type",
                "SecureString",
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
  - name: ssm5
    description: Desc
    type: SecureString
    kms: {KEY_ARN1}
secrets:
  - name: secret1
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
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
  - name: ssm5
    value: SecretData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.decrypt")
@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_update_exists_parameter(
    mock_prompt,
    mock_encrypt,
    mock_decrypt,
    mock_cli_runner,
):
    """
    Should update an existing SSM parameter
    """
    mock_decrypt.return_value = b"SecretData"
    mock_prompt.side_effect = ["Desc", "PlainText"]

    mock_encrypt.return_value = b"ChangedData"
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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm1",
                "--type",
                "SecureString",
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
    description: Desc
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
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
parameters:
  - name: ssm1
    value: ChangedData
"""
            )
        mock_encrypt.assert_called_once_with(ANY, "PlainText", KEY_ARN)


@patch("aws_secrets.miscellaneous.kms.encrypt")
@patch("aws_secrets.cli.set_parameter.prompt")
def test_set_parameter_cli_update_exists_parameter_string(
    mock_prompt,
    mock_encrypt,
    mock_cli_runner,
):
    """
    Should update an existing SSM parameter type String
    """
    mock_prompt.side_effect = ["Desc", "PlainText"]
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
                "set-parameter",
                "--env-file",
                config_file,
                "--name",
                "ssm2",
                "--type",
                "String",
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
    value: PlainText
    description: Desc
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
"""
            )

        with open(secrets_file, "r") as secrets:
            assert (
                secrets.read()
                == """\
secrets:
  - name: secret1
    value: SecretData
parameters:
  - name: ssm1
    value: SecretData
"""
            )
        mock_encrypt.assert_not_called()
