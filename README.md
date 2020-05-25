# AWS Secrets CLI

## About

AWS Secrets CLI is a tool to manage [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) (SecureString and String) using KMS to encrypt your information. this tool enables you to store your secrets information without expose into your git repository.

## Motivation

When you need to manage SSM parameter (SecureString) in multiple AWS Environments you need to create or update manually, because [CloudFormation](https://aws.amazon.com/pt/cloudformation/) doesn't support SSM parameter type Secure, you can use AWS CLI or boto3 to create the parameters for you, but you need to read the secrets values from somewhere, and you can't store into your git repository.

AWS Secrets CLI provides you a Command Line Interface that manage your secrets using [KMS](https://aws.amazon.com/pt/kms/), so you can store the config file into your git repository because your secrets will not expore, only for people that have access to KMS Key.

## Getting Started

### Install

```shell
pip install aws-secrets-cli
```

### Requirements

It is necessary to create a KMS key before starting to create the parameter using the CLI.

You can create this key using AWS CLI, AWS SDK, console or CloudFormation:

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

### Our fist config.

For naming convention you should give the environment name for the file name (e.g dev.yaml)

```yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
```

### Add our first secure parameter

For create your first parameter you need to provide the environment file name that you create on the last step (`--env-file`), the parameter name (`--parameter`), the value (`--value`) and optionally you can provide AWS profile and region.

```shell
aws-secrets set-parameter --env-file dev.yaml --parameter /foo/dev/password --value "FooData" --profile myaws-profile --region eu-west-1
```

>
> This command can be used for modify parameters.

Now open your config file and you should see `parameters` property with the parameter that you create using the command above.

``` yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
parameters:
- name: /foo/dev/password  
  type: SecureString
  value: <encrypted_data>
```

>
> You can modify or add parameters directly in the configuration file.

### Create parameters into AWS Account

To deploy the parameter that you created on last step, you need to execute this command:

``` shell
aws-secrets deploy --env-file dev.yaml --profile myaws-profile --region eu-west-1
```

Now your parameters have been created in AWS Account.