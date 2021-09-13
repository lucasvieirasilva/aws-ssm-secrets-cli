import os
import pathlib

import boto3
import botocore
import pytest


@pytest.fixture(autouse=True)
def setup_aws_credentials_env_vars():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    boto3.setup_default_session(region_name=os.getenv('AWS_REGION', 'us-east-1'))


@pytest.fixture
def boto_fs(fs):
    for module in [boto3, botocore]:
        module_dir = pathlib.Path(module.__file__).parent
        print(module.__file__)
        fs.add_real_directory(module_dir, lazy_read=False)

    yield fs
