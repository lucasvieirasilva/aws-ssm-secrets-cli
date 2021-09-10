import os

import boto3
import pytest


@pytest.fixture(autouse=True)
def setup_aws_credentials_env_vars():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    boto3.setup_default_session(region_name=os.getenv('AWS_REGION', 'us-east-1'))
