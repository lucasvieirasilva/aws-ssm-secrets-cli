from setuptools import setup, find_packages

install_requirements = [
    "boto3",
    "click"
]

setup(
    name="aws-ssm-secrets-cli",
    version='0.0.14',
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
