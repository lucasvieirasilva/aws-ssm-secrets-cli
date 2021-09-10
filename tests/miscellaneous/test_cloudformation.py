import datetime
from unittest import mock

import boto3
import pytest
from aws_secrets.helpers.catch_exceptions import CLIError
from aws_secrets.miscellaneous import cloudformation
from botocore.stub import Stubber


def test_get_output_value_with_stack_not_exists():
    """
        Should throw an exception when the stack not exists
    """

    client = boto3.client('cloudformation')
    stack_name = 'mystack'

    with mock.patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            stubber.add_response('describe_stacks', {
                'Stacks': []
            }, {
                'StackName': stack_name
            })

            mock_client.return_value = client

            with pytest.raises(CLIError) as error:
                cloudformation.get_output_value(boto3.Session(), stack_name, 'out1')

            assert f'{stack_name} not found' == str(error.value)


def test_get_output_value_with_output_not_exists():
    """
        Should throw an exception when the output not exists
    """

    client = boto3.client('cloudformation')
    stack_name = 'mystack'

    with mock.patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            stubber.add_response('describe_stacks', {
                'Stacks': [{
                    'StackName': stack_name,
                    'CreationTime': datetime.datetime.now(),
                    'StackStatus': "CREATE_COMPLETE",
                    'Outputs': []
                }]
            }, {
                'StackName': stack_name
            })

            mock_client.return_value = client

            with pytest.raises(CLIError) as error:
                cloudformation.get_output_value(boto3.Session(), stack_name, 'out1')

            assert f'output out1 not found on stack {stack_name}' == str(error.value)


def test_get_output_value():
    """
        Should get the output value successfully
    """

    client = boto3.client('cloudformation')
    stack_name = 'mystack'
    value = 'myvalue'

    with mock.patch.object(boto3.Session, 'client') as mock_client:
        with Stubber(client) as stubber:
            stubber.add_response('describe_stacks', {
                'Stacks': [{
                    'StackName': stack_name,
                    'CreationTime': datetime.datetime.now(),
                    'StackStatus': "CREATE_COMPLETE",
                    'Outputs': [{
                        'OutputKey': 'out1',
                        'OutputValue': value
                    }]
                }]
            }, {
                'StackName': stack_name
            })

            mock_client.return_value = client

            assert cloudformation.get_output_value(boto3.Session(), stack_name, 'out1') == value
