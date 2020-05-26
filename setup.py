from setuptools import setup, find_packages

setup(
    name="aws-ssm-secrets-cli",
    version='0.0.6',
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
    install_requires=[
        'boto3',
    ],
    entry_points='''
        [console_scripts]
        aws-secrets=aws_secrets.cli:main
    ''',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ]
)
