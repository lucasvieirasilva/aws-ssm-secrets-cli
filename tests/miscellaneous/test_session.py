from boto3.session import Session
from aws_secrets.miscellaneous import session


def test_session():
    """
        Should returns the boto3 session object
    """
    session.aws_profile = None
    session.aws_region = 'us-east-1'

    assert isinstance(session.session(), Session)
