import boto3

global aws_region
global aws_profile
aws_region = ''
aws_profile = ''


def session():
    return boto3.session.Session(
        region_name=aws_region, profile_name=aws_profile)
