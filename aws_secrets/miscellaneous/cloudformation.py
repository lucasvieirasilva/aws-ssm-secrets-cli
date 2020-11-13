def get_output_value(session, stack_name, output_name):
    cf = session.client('cloudformation')
    stack_response = cf.describe_stacks(
        StackName=stack_name
    )

    if len(stack_response['Stacks']) == 0:
        raise Exception(f'{stack_name} not found')

    outputs = stack_response['Stacks'][0]['Outputs']

    output = next(
        (output for output in outputs if output['OutputKey'] == output_name), None)

    if output is None:
        raise Exception(f'output {output_name} not found on stack {stack_name}')

    return output['OutputValue']
