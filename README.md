# AWS Secrets CLI

## About

AWS Secrets CLI is a tool to manage [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) (SecureString and String) using KMS to encrypt your information. This tool enables you to store your secrets information without exposing it to your git repository.

## Motivation

When you need to manage SSM parameter (SecureString) in multiple AWS Environments you need to create or update manually, because [CloudFormation](https://aws.amazon.com/pt/cloudformation/) doesn't support SSM parameter type Secure, you can use AWS CLI or boto3 to establish the parameters for you, but you need to read the secrets values from somewhere. You can't store into your git repository.

AWS Secrets CLI provides you a Command Line Interface that manages your secrets using [KMS](https://aws.amazon.com/pt/kms/), so you can store the config file into your git repository because your secrets will not expose, only for people that have access to KMS Key.

## Getting Started

### Install

```shell
pip install aws-ssm-secrets-cli
```

### Requirements

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
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Resource: "*"
          - Action:
              - kms:Decrypt
              - kms:Encrypt
              - kms:ReEncrypt*
              - kms:GenerateDataKey*
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
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

### Getting Started

#### Our fist config

For naming convention, you should give the environment name for the file name (e.g., dev.yaml)

```yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
parameters:
- name: myparametername
  value: 'MySecretValueHere'
  type: SecureString
secrets:
- name: mysecretname
  value: 'MySecretValueHere' # or value: 
                             #      prop: 'Value' 
```

#### Encrypt

To encrypt the parameter values, you need to use this command:

``` shell
aws-secrets encrypt -e dev.yaml --profile myprofile --region eu-west-1
```

#### Decrypt

To edit the values, you can decrypt and re-encrypt the parameter values. You need to use this command:

``` shell
aws-secrets decrypt -e dev.yaml --profile myprofile --region eu-west-1
```

At this moment, a new file has created `dev.yaml.dec`. If you want to decrypt in overwrite mode put the `--output` option with the same file name that you are decrypting.

``` shell
aws-secrets decrypt -e dev.yaml --output dev.yaml --profile myprofile --region eu-west-1
```

After your changes you need to re-encrypt, you can do it using this command:

``` shell
aws-secrets encrypt -e dev.yaml --profile myprofile --region eu-west-1
```

#### Create parameters into AWS Account

To deploy the parameter that you created on the last step, you need to execute this command:

``` shell
aws-secrets deploy -e dev.yaml --profile myaws-profile --region eu-west-1
```

Now your parameters have been created in AWS Account.

### Command Line Interface

Command options differ depending on the command, and can be found by running:

``` shell
aws-secrets --help
aws-secrets COMMAND --help
```

### encrypt

To encrypt SecureString parameters and secrets values in the environment file.

``` shell
aws-secrets encrypt
  --env-file 
  [--profile]
  [--region]
```

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### decrypt

To decrypt SecureString parameters and secrets values in the environment file.

``` shell
aws-secrets decrypt
  --env-file 
  [--profile]
  [--region]
```

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### set-parameter

Create or modify the SSM parameter in the environment file.

``` shell
aws-secrets set-parameter 
  --env-file 
  --name
  [--kms]
  [--type]
  [--profile]
  [--region]
```

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--name` or `-n` | SSM Parameter Name | `String` | `true` |  |  |
| `--type` or `-t` | SSM Parameter Type | `String` | `true` | `String` and `SecureString` | `SecureString` |
| `--kms` or `-k` | KMS Id or ARN | `String` | `true` |  |  |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### set-secret

Create or modify secrets in the environment file.

``` shell
aws-secrets set-secret
  --env-file 
  --name
  [--kms]
  [--profile]
  [--region]
```

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--name` or `-n` | SSM Parameter Name | `String` | `true` |  |  |
| `--kms` or `-k` | KMS Id or ARN | `String` | `true` |  |  |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### view-parameter

View the SSM parameter value in the environment file.

``` shell
aws-secrets view-parameter
  --env-file 
  --name
  [--non-decrypt]
  [--profile]
  [--region]
```

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--name` or `-n` | SSM Parameter Name | `String` | `true` |  |  |
| `--non-decrypt` | Used when you want to view an SecureString value without decrypt | `Boolean` | `false` |  | `false` |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### deploy

Create or update SSM parameters and secrets in the AWS Account.

``` shell
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

### Options

| Option | Description | Data Type | Required | Options | Default |
|--|--|--|--|--|--|
| `--env-file` or `-e` | Environment file path | `String` | `true` |
| `--filter-pattern` | Filter Pattern (e.g `/app/db/*/password` match with `/app/db/dev/password` or `/app/db/prod/password` ) | `String` | `false` |
| `--dry-run` | Execution without apply the changes on the environment | `Boolean` | `false` |  | `false` |
| `--confirm` | Confirm prompt before apply the changes | `Boolean` | `false` |  | `false` |
| `--only-secrets` | Apply changes just for AWS Secrets | `Boolean` | `false` |  | `false` |
| `--only-parameters` |  Apply changes just for SSM Parameters | `Boolean` | `false` |  | `false` |
| `--profile` | AWS Profile | `String` | `false` |  |  |
| `--region` | AWS Region | `String` | `false` |  |  |

### Resolvers

This CLI implements resolvers, which can be used to resolve the value of a command output or a CloudFormation output value.

#### !cf_output

This resolver can be used in `parameters[*].value`, `secrets[*].value` and `kms.arn` properties.

Example:

```yaml
kms:
  arn: !cf_output 'mystack.MyOutputKey'
parameters:
  - name: myparameter-name
    type: String
    value: !cf_output 'mystack.MyOutputKey'
```

#### !cmd

This resolver can be used in `parameters[*].value` and `secrets[*].value` properties.

Example:

```yaml
kms:
  arn: 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
parameters:
  - name: myparameter-name
    type: SecureString
    value: !cmd 'echo "Teste"'
    decryptOnDeploy: false
```

>
> If you use `!cmd` resolver with `SecureString`, you must disable the decryption action on the deployment. Otherwise, the CLI will try to decrypt the resolved value, and the process will be failed.

##### providers

###### cf

CloudFormation Stack Output resolver

Usage

```text
${cf:stack-name.output-name}
```

###### session

AWS Credentials Session resolver

Usage

```text
${session:profile} or ${session:region}
```

### Global Tags

You also can include Tags on a global level:

```yaml
tags:
  SomeKey: SomeValue
kms:
  arn: 'arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab'
parameters:
  ...
secrets:
  ...
```
