from botocore.session import Session

from aws_secrets.helpers.catch_exceptions import CLIError


def get_output_value(
    session: Session,
    stack_name: str,
    output_name: str
) -> str:
    """
        Get CloudFormation output value by output name

        Args:
            session (`session`): Boto3 session object
            stack_name (`str`): CloudFormation stack name
            output_name (`str`): CloudFormation stack output name

        Returns:
            `str`: CloudFormation stack output value
    """
    cf = session.client('cloudformation')
    stack_response = cf.describe_stacks(
        StackName=stack_name
    )

    if len(stack_response['Stacks']) == 0:
        raise CLIError(f'{stack_name} not found')

    outputs = stack_response['Stacks'][0]['Outputs']

    output = next(
        (output for output in outputs if output['OutputKey'] == output_name), None)

    if output is None:
        raise CLIError(f'output {output_name} not found on stack {stack_name}')

    return output['OutputValue']
