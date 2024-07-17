import boto3
from botocore.session import Session

global aws_region
global aws_profile
aws_region = ''
aws_profile = ''


def session() -> Session:
    """
        Get boto3 session object

        Returns:
            `Session`: boto3 session object
    """
    return boto3.session.Session(
        region_name=aws_region if aws_region else None, profile_name=aws_profile if aws_profile else None)
