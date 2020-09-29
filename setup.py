from setuptools import setup, find_packages
from aws_secrets import __version__

install_requirements = [
    "boto3>=1.3,<2.0",
    "click>=7.0,<8.0",
    "PyYaml>=5.1,<6.0"
]

setup(
    name="aws-ssm-secrets-cli",
    version=__version__,
    license='MIT',
    description = 'AWS Secret CLI for manage SSM SecureString and SecretsManager',
    long_description = open("README.md", "r").read(),
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    long_description_content_type='text/markdown',
    author = 'Lucas Vieira',
    author_email = 'lucas.vieira94@outlook.com',
    url = 'https://github.com/lucasvieirasilva/aws-ssm-secrets-cli',
    keywords = ['AWS', 'SECRETS', 'SSM', 'MANAGER'],
    install_requires=install_requirements,
    entry_points={
        "console_scripts": [
            'aws-secrets=aws_secrets.cli.cli:cli'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ]
)
