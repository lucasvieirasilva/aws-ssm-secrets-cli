from typing import Optional

import click
from click.core import Context
from prompt_toolkit import HTML, prompt

from aws_secrets.config.config_reader import ConfigReader
from aws_secrets.helpers.catch_exceptions import catch_exceptions
from aws_secrets.miscellaneous import session
from aws_secrets.miscellaneous.prompt import (
    DEFAULT_PROMPT_SYLE, get_multiline_input_save_keyboard, radiolist_prompt)


@click.command(name="set-parameter", help="Add/Update SSM Parameters")
@click.option("-e", "--env-file", type=click.Path(), required=True)
@click.option("-n", "--name", required=False)
@click.option("-d", "--description", help="SSM Parameter Description", required=False)
@click.option("-v", "--value", help="SSM Parameter Value", required=False)
@click.option(
    "-t",
    "--type",
    required=False,
    type=click.Choice(["String", "SecureString"], case_sensitive=True),
)
@click.option("-k", "--kms")
@click.option("--profile", help="AWS Profile", envvar="AWS_PROFILE")
@click.option("--region", help="AWS Region", envvar="AWS_REGION")
@click.pass_context
@catch_exceptions
def set_parameter(
    ctx: Context,
    env_file: str,
    name: Optional[str],
    description: Optional[str],
    value: Optional[str],
    type: Optional[str],
    kms: Optional[str],
    profile: Optional[str],
    region: Optional[str],
):
    """
    Add/Update SSM Parameters CLI Commmand `aws-secrets set-parameter --help`

    Args:
        ctx (`Context`): click context object
        env_file (`str`): configuration YAML file
        name (`str`, optional): SSM parameter name
        description (`str`, optional): SSM parameter description
        type (`str`, optional): SSM parameter type
        kms (`str`, optional): SSM parameter KMS Arn or Id
        profile (`str`, optional): AWS Profile
        region (`str`, optional): AWS Region
    """
    ctx.obj["config_file"] = env_file
    session.aws_profile = profile
    session.aws_region = region
    config = ConfigReader(env_file)
    provider = config.get_provider("parameters")

    context_data = {"name": name}
    if not name:
        context_data["name"] = prompt(
            HTML(
                "<question><question_mark>?</question_mark> What is the name of the SSM parameter? </question>"
            ),
            style=DEFAULT_PROMPT_SYLE,
        )

    parameter = provider.find(context_data["name"])

    if description:
        context_data["description"] = description
    else:
        context_data["description"] = prompt(
            HTML(
                "<question><question_mark>?</question_mark> What is the description of the parameter? </question>"
            ),
            default=parameter.description if parameter else "",
            style=DEFAULT_PROMPT_SYLE,
        )

    if type:
        context_data["type"] = type
    else:
        context_data["type"] = radiolist_prompt(
            title=HTML(
                "<question><question_mark>?</question_mark> What is the type of the parameter? </question>"
            ),
            values=[
                ("String", "String"),
                ("SecureString", "SecureString"),
            ],
            default=parameter.type if parameter else "SecureString",
        )

    if kms:
        context_data["kms"] = kms

    if not value:
        initial_value = ""
        if parameter is not None:
            initial_value = parameter.decrypt(format=True)

        click.echo(
            f"Press {get_multiline_input_save_keyboard()} or [Esc] followed by [Enter] to accept input."
        )
        input_value = prompt("", multiline=True, default=initial_value)
        if input_value.strip() == "":
            return

        context_data["value"] = input_value
    else:
        context_data["value"] = value

    if parameter is None:
        parameter = provider.add(context_data)
    else:
        provider.update(context_data)

    config.encrypt()
    config.save()
