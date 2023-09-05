# AWS Secrets CLI

## SonarCloud Status

[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=bugs)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=code_smells)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=sqale_index)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=ncloc)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=security_rating)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=lucasvieirasilva_aws-ssm-secrets-cli&metric=alert_status)](https://sonarcloud.io/dashboard?id=lucasvieirasilva_aws-ssm-secrets-cli)

## About

AWS Secrets CLI is a tool to manage [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) (SecureString and String) using KMS to encrypt your information. This tool enables you to store your secrets information without exposing it to your git repository.

## Motivation

When you need to manage SSM parameter (SecureString) in multiple AWS Environments you need to create or update manually, because [CloudFormation](https://aws.amazon.com/pt/cloudformation/) doesn't support SSM parameter type Secure, you can use AWS CLI or boto3 to establish the parameters for you, but you need to read the secrets values from somewhere. You can't store into your git repository.

AWS Secrets CLI provides you a Command Line Interface that manages your secrets using [KMS](https://aws.amazon.com/pt/kms/), so you can store the config file into your git repository because your secrets will not expose, only for people that have access to KMS Key.

## Install

```shell
pip install aws-ssm-secrets-cli
```

## Requirements

It is necessary to create a KMS key before starting to create the parameter using the CLI.

You can create this key using AWS CLI, AWS SDK, console, or CloudFormation:

Example using CloudFormation:

```yaml
Description: "KMS Key for Secrest"
Resources:
  Key:
    Type: AWS::KMS::Key
    Properties:
      KeyPolicy:
        Statement:
          - Action:
              - kms:Create*
              - kms:Describe*
              - kms:Enable*
              - kms:List*
              - kms:Put*
              - kms:Update*
              - kms:Revoke*
              - kms:Disable*
              - kms:Get*
              - kms:Delete*
              - kms:ScheduleKeyDeletion
              - kms:CancelKeyDeletion
              - kms:GenerateDataKey
              - kms:TagResource
              - kms:UntagResource
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Resource: "*"
          - Action:
              - kms:Decrypt
              - kms:Encrypt
              - kms:ReEncrypt*
              - kms:GenerateDataKey*
            Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Resource: "*"
        Version: "2012-10-17"
      Description: AWS KMS Key for secrets
    UpdateReplacePolicy: Retain
    DeletionPolicy: Retain

  KeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: alias/infra-scripts-secrets
      TargetKeyId: !GetAtt Key.Arn

Outputs:
  KeyArn:
    Description: KMS Key Arn
    Value: !GetAtt Key.Arn
```

## Getting Started

### Our fist config

For naming convention, you should give the environment name for the file name (e.g., dev.yaml)

```yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
encryption_sdk: "aws_encryption_sdk"
parameters:
  - name: myparametername
    value: "MySecretValueHere"
    type: SecureString
secrets:
  - name: mysecretname
    value: "MySecretValueHere"
```

or AWS Secrets manager with object

```yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
encryption_sdk: "aws_encryption_sdk"
parameters:
  - name: myparametername
    value: "MySecretValueHere"
    type: SecureString
secrets:
  - name: mysecretname
    value:
      user: myusername
      password: mypassword
```

### Encrypt

To encrypt the parameter values, you need to use this command:

```shell
aws-secrets encrypt -e dev.yaml --profile myprofile --region eu-west-1
```

### Decrypt

To edit the values, you can decrypt and re-encrypt the parameter values. You need to use this command:

```shell
aws-secrets decrypt -e dev.yaml --profile myprofile --region eu-west-1
```

At this moment, a new file has created `dev.yaml.dec`. If you want to decrypt in overwrite mode put the `--output` option with the same file name that you are decrypting.

```shell
aws-secrets decrypt -e dev.yaml --output dev.yaml --profile myprofile --region eu-west-1
```

After your changes you need to re-encrypt, you can do it using this command:

```shell
aws-secrets encrypt -e dev.yaml --profile myprofile --region eu-west-1
```

### Create parameters into AWS Account

To deploy the parameter that you created on the last step, you need to execute this command:

```shell
aws-secrets deploy -e dev.yaml --profile myaws-profile --region eu-west-1
```

Now your parameters have been created in AWS Account.

## Migrate KMS API to AWS Encryption SDK

The AWS Encryption SDK is a client-side encryption library designed to make it easy for everyone to encrypt and decrypt data using industry standards and best practices. It enables you to focus on the core functionality of your application, rather than on how to best encrypt and decrypt your data. The AWS Encryption SDK is provided free of charge under the Apache 2.0 license.

Full documentation: <https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/introduction.html>

Using AWS Encryption enables AWS Secrets CLI to encrypt data with more than 4KB.

### Migration process

1. Decrypt all SSM parameter and Secrets manager:

```shell
aws-secrets decrypt -e dev.yaml --output dev.yaml --profile myprofile --region eu-west-1
```

2. Update YAML configuration to add the `encryption_sdk` with `aws_encryption_sdk` value.

```yaml
kms:
  arn: KMS_KEY_ARN
encryption_sdk: "aws_encryption_sdk"
parameters:
  - name: myparametername
    value: "MySecretValueHere"
    type: SecureString
secrets:
  - name: mysecretname
    value: "MySecretValueHere"
```

> Currently, the default value is `boto3`

3. Re-encrypt the YAML configuration file

```shell
aws-secrets encrypt -e dev.yaml --profile myprofile --region eu-west-1
```

## Configuration Schema

```yaml
tags: # Global tags, applied to all the resources
  key: 'string' # key/value pair
kms:
  arn: 'string' # Required, KMS ARN
encryption_sdk: 'aws_encryption_sdk' | 'boto3'
parameters: # AWS SSM Parameter Section
  - name: 'string' # Required, Parameter Name
    description: 'string' # Optional, Parameter Description
    type: 'String|SecureString' # Required, Parameter Type
    value: 'string' # Required only for Type 'String' or if it is some YAML tag (e.g. !file or !cmd)
    tier: 'Standard|Advanced|Intelligent-Tiering' # Optional, Parameter Tier, default 'Standard'
    tags: # Optional, Parameter Tags, it is extended with the global tags
      key: 'string'
secrets: # AWS Secrets Manager secrets Section
  - name: 'string' # Required, Secret Name
    description: 'string' # Optional, Secret Description
    value: 'string' # Required only if it is some YAML tag (e.g. !file or !cmd)
    tags: # Optional, Secret Tags, it is extended with the global tags
      key: 'string'
secrets_file: 'Path' # Optional, Secrets file path, default '<config-filename>.secrets.yaml'
```

## Command Line Interface

Command options differ depending on the command, and can be found by running:

```shell
aws-secrets --help
aws-secrets COMMAND --help
```

### encrypt

To encrypt SecureString parameters and secrets values in the environment file.

```shell
aws-secrets encrypt
  --env-file
  [--profile]
  [--region]
```

#### Options

| Option               | Description           | Data Type | Required | Options | Default |
| -------------------- | --------------------- | --------- | -------- | ------- | ------- |
| `--env-file` or `-e` | Environment file path | `String`  | `true`   |         |         |
| `--profile`          | AWS Profile           | `String`  | `false`  |         |         |
| `--region`           | AWS Region            | `String`  | `false`  |         |         |

### decrypt

To decrypt SecureString parameters and secrets values in the environment file.

```shell
aws-secrets decrypt
  --env-file
  [--profile]
  [--region]
```

#### Options

| Option               | Description           | Data Type | Required | Options | Default |
| -------------------- | --------------------- | --------- | -------- | ------- | ------- |
| `--env-file` or `-e` | Environment file path | `String`  | `true`   |         |         |
| `--profile`          | AWS Profile           | `String`  | `false`  |         |         |
| `--region`           | AWS Region            | `String`  | `false`  |         |         |

### set-parameter

Create or modify the SSM parameter in the environment file.

```shell
aws-secrets set-parameter
  --env-file
  --name
  [--description]
  [--kms]
  [--type]
  [--profile]
  [--region]
```

#### Options

| Option                  | Description               | Data Type | Required | Options                     | Default        |
| ----------------------- | ------------------------- | --------- | -------- | --------------------------- | -------------- |
| `--env-file` or `-e`    | Environment file path     | `String`  | `true`   |
| `--name` or `-n`        | SSM Parameter Name        | `String`  | `true`   |                             |                |
| `--description` or `-d` | SSM Parameter Description | `String`  | `false`  |                             |                |
| `--type` or `-t`        | SSM Parameter Type        | `String`  | `true`   | `String` and `SecureString` | `SecureString` |
| `--kms` or `-k`         | KMS Id or ARN             | `String`  | `true`   |                             |                |
| `--profile`             | AWS Profile               | `String`  | `false`  |                             |                |
| `--region`              | AWS Region                | `String`  | `false`  |                             |                |

### set-secret

Create or modify secrets in the environment file.

```shell
aws-secrets set-secret
  --env-file
  --name
  [--description]
  [--kms]
  [--profile]
  [--region]
```

#### Options

| Option                  | Description           | Data Type | Required | Options | Default |
| ----------------------- | --------------------- | --------- | -------- | ------- | ------- |
| `--env-file` or `-e`    | Environment file path | `String`  | `true`   |         |         |
| `--name` or `-n`        | Secret Name           | `String`  | `true`   |         |         |
| `--description` or `-d` | Secret Description    | `String`  | `false`  |         |         |
| `--kms` or `-k`         | KMS Id or ARN         | `String`  | `true`   |         |         |
| `--profile`             | AWS Profile           | `String`  | `false`  |         |         |
| `--region`              | AWS Region            | `String`  | `false`  |         |         |

### view-parameter

View the SSM parameter value in the environment file.

```shell
aws-secrets view-parameter
  --env-file
  --name
  [--profile]
  [--region]
```

#### Options

| Option               | Description           | Data Type | Required | Options | Default |
| -------------------- | --------------------- | --------- | -------- | ------- | ------- |
| `--env-file` or `-e` | Environment file path | `String`  | `true`   |         |         |
| `--name` or `-n`     | SSM Parameter Name    | `String`  | `true`   |         |         |
| `--profile`          | AWS Profile           | `String`  | `false`  |         |         |
| `--region`           | AWS Region            | `String`  | `false`  |         |         |

### deploy

Create or update SSM parameters and secrets in the AWS Account.

```shell
aws-secrets deploy
  --env-file
  [--filter-pattern]
  [--dry-run]
  [--confirm]
  [--only-secrets]
  [--only-parameters]
  [--profile]
  [--region]
```

#### Options

| Option               | Description                                                                                             | Data Type | Required | Options | Default |
| -------------------- | ------------------------------------------------------------------------------------------------------- | --------- | -------- | ------- | ------- |
| `--env-file` or `-e` | Environment file path                                                                                   | `String`  | `true`   |         |         |
| `--filter-pattern`   | Filter Pattern (e.g `/app/db/*/password` match with `/app/db/dev/password` or `/app/db/prod/password` ) | `String`  | `false`  |         |         |
| `--dry-run`          | Execution without apply the changes on the environment                                                  | `Boolean` | `false`  |         | `false` |
| `--confirm`          | Confirm prompt before apply the changes                                                                 | `Boolean` | `false`  |         | `false` |
| `--only-secrets`     | Apply changes just for AWS Secrets                                                                      | `Boolean` | `false`  |         | `false` |
| `--only-parameters`  | Apply changes just for SSM Parameters                                                                   | `Boolean` | `false`  |         | `false` |
| `--profile`          | AWS Profile                                                                                             | `String`  | `false`  |         |         |
| `--region`           | AWS Region                                                                                              | `String`  | `false`  |         |         |

#### Resolvers

This CLI implements resolvers, which can be used to resolve the value of a command output or a CloudFormation output value.

##### !file

This resolver is designed to load a file content to the SSM Parameter or Secrets Manager Value.

Example:

```yaml

---
secrets:
  - name: mysecret
    value: !file myfile.txt
```

##### !cf_output

This resolver can be used in `parameters[*].value`, `secrets[*].value` and `kms.arn` properties.

Example:

```yaml
kms:
  arn: !cf_output "mystack.MyOutputKey"
parameters:
  - name: myparameter-name
    type: String
    value: !cf_output "mystack.MyOutputKey"
```

```yaml
kms:
  arn: !cf_output "mystack.MyOutputKey.us-east-1"
parameters:
  - name: myparameter-name
    type: String
    value: !cf_output "mystack.MyOutputKey.us-east-1"
```

##### !cmd

This resolver can be used in `parameters[*].value` and `secrets[*].value` properties.

Example:

```yaml
kms:
  arn: "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
parameters:
  - name: myparameter-name
    type: SecureString
    value: !cmd 'echo "Teste"'
```

###### providers

###### cf

CloudFormation Stack Output resolver

Usage

```text
${cf:stack-name.output-name}
```

With default values

```text
${cf:stack-name.output-name, 'mydefaultvalue'}
```

###### session

AWS Credentials Session resolver

Usage

```text
${session:profile} or ${session:region}
```

With default values

```text
${session:profile, 'myprofile'} or ${session:region, 'us-east-1'}
```

###### aws

AWS Provider resolves the AWS CLI `--profile` and `--region` based on the `aws-secrets` CLI.

Usage

```text
${aws:profile} or ${aws:region}
```

With default values

```text
${aws:profile, 'myprofile'} or ${aws:region, 'us-east-1'}
```

**Example**:

With the config file:

```yaml
kms:
  arn: !cf_output "mystack.KeyArn"
parameters:
  - description: My SSM Parameter
    name: /my/ssm/param
    type: SecureString
    value: !cmd 'aws s3 ls ${aws:profile} ${aws:region, "eu-west-1"}'
```

When run the `aws-secrets` with the `--profile` or `--region`

```shell
aws-secrets -e conf.yaml --profile myprofile --region us-east-1
```

The AWS CLI command will be execute this command:

```shell
aws s3 ls --profile myprofile --region us-east-1
```

If `--profile` not be speficied in the `aws-secrets` execution, like this:

```shell
aws-secrets -e conf.yaml --region us-east-1
```

The AWS CLI command will be execute this command:

```shell
aws s3 ls --region eu-west-1
```

> The `--region` continue in the command because the resolver has the default value with `eu-west-1` in the config file.

### Global Tags

You also can include Tags on a global level:

```yaml
tags:
  SomeKey: SomeValue
kms:
  arn: "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
parameters: ...
secrets: ...
```
