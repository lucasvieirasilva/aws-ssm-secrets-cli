import logging
import textwrap
from typing import Optional

import click
from click.core import Context
from prompt_toolkit import HTML, prompt

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session
from aws_secrets.miscellaneous.prompt import (
    DEFAULT_PROMPT_SYLE, get_multiline_input_save_keyboard)

logger = logging.getLogger(__name__)


@click.command(name="set-secret", help="Add/Update AWS Secrets Manager secrets")
@click.option("-e", "--env-file", type=click.Path(), required=True)
@click.option("-n", "--name", required=False)
@click.option("-d", "--description", help="Secret Description", required=False)
@click.option("-v", "--value", help="Secret Value", required=False)
@click.option("-k", "--kms")
@click.option("--profile", help="AWS Profile", envvar="AWS_PROFILE")
@click.option("--region", help="AWS Region", envvar="AWS_REGION")
@click.pass_context
@catch_exceptions
def set_secret(
    ctx: Context,
    env_file: str,
    name: Optional[str],
    description: Optional[str],
    value: Optional[str],
    kms: Optional[str],
    profile: Optional[str],
    region: Optional[str],
):
    """
    Add/Update AWS Secrets Manager secrets CLI Commmand `aws-secrets set-secret --help`

    Args:
        ctx (`Context`): click context object
        env_file (`str`): configuration YAML file
        name (`str`, optional): SSM parameter name
        description (`str`, optional): SSM parameter description
        kms (`str`, optional): SSM parameter KMS Arn or Id
        profile (`str`, optional): AWS Profile
        region (`str`, optional): AWS Region
    """
    ctx.obj["config_file"] = env_file
    session.aws_profile = profile
    session.aws_region = region

    config = ConfigReader(env_file)
    provider = config.get_provider("secrets")

    context_data = {"name": name}
    if not name:
        context_data["name"] = prompt(
            HTML(
                "<question><question_mark>?</question_mark> What is the name of the secret? </question>"
            ),
            style=DEFAULT_PROMPT_SYLE,
        )

    secret = provider.find(context_data["name"])

    if description:
        context_data["description"] = description
    else:
        context_data["description"] = prompt(
            HTML(
                "<question><question_mark>?</question_mark> What is the description of the secret? </question>"
            ),
            default=secret.description if secret else "",
            style=DEFAULT_PROMPT_SYLE,
        )

    if kms:
        context_data["kms"] = kms

    if not value:
        initial_value = ""
        if secret is not None:
            initial_value = secret.decrypt(format=True)

        input_value = prompt(
            HTML(
                textwrap.dedent(f"""\
                    <question><question_mark>?</question_mark> What is the value of the secret?
                    Press {get_multiline_input_save_keyboard()} or [Esc] followed by [Enter] to accept input.
                    </question>
                    """)
            ),
            multiline=True,
            default=initial_value,
            style=DEFAULT_PROMPT_SYLE,
        )
        if input_value.strip() == "":
            return

        context_data["value"] = input_value
    else:
        context_data["value"] = value

    if secret is None:
        secret = provider.add(context_data)
    else:
        provider.update(context_data)

    config.encrypt()
    config.save()
