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

### Getting Started

#### Our fist config.

For naming convention you should give the environment name for the file name (e.g dev.yaml)

```yaml
kms:
  arn: KMS_KEY_ARN (String) #Required
```

#### Add our first secure parameter

For create your first parameter you need to provide the environment file name that you create on the last step (`--env-file`), the parameter name (`--parameter`), the value (`--value`) and optionally you can provide AWS profile and region.

```shell
aws-secrets set-parameter -e dev.yaml -n /foo/dev/password -v "FooData" --profile myaws-profile --region eu-west-1
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

#### Create parameters into AWS Account

To deploy the parameter that you created on last step, you need to execute this command:

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

### set-parameter

Create or modify SSM parameter in environment file.

``` shell
aws-secrets set-parameter 
  --env-file 
  --name
  --value
  [--type]
  [--profile]
  [--region]
```

### Options

**Parameter**: `--env-file` or `-e`

**Description**: Environment file path

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--name` or `-n`

**Description**: SSM Parameter Name

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--value` or `-v`

**Description**: SSM Parameter Value

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--type` or `-t`

**Description**: SSM Parameter Type

**Data Type**: `String`

**Options**: `String` and `SecureString`

**Default**: `SecureString`

**Required**: `true`

---

**Parameter**: `--profile`

**Description**: AWS Profile

**Data Type**: `String`

**Required**: `false`

---

**Parameter**: `--region`

**Description**: AWS Region

**Data Type**: `String`

**Required**: `false`

### set-secret

Create or modify secrets in environment file.

``` shell
aws-secrets set-secret
  --env-file 
  --name
  --value
  [--profile]
  [--region]
```

### Options

**Parameter**: `--env-file` or `-e`

**Description**: Environment file path

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--name` or `-n`

**Description**: Secret Name

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--value` or `-v`

**Description**: Secret Value

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--profile`

**Description**: AWS Profile

**Data Type**: `String`

**Required**: `false`

---

**Parameter**: `--region`

**Description**: AWS Region

**Data Type**: `String`

**Required**: `false`

### view-parameter

View SSM parameter value in environment file.

``` shell
aws-secrets view-parameter
  --env-file 
  --name
  [--non-decrypt]
  [--profile]
  [--region]
```

### Options

**Parameter**: `--env-file` or `-e`

**Description**: Environment file path

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--name` or `-n`

**Description**: Secret Name

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--non-decrypt`

**Description**: Used when you want to view an SecureString value without decrypt

**Data Type**: `Boolean`

**Default**: `false`

**Required**: `false`

---

**Parameter**: `--profile`

**Description**: AWS Profile

**Data Type**: `String`

**Required**: `false`

---

**Parameter**: `--region`

**Description**: AWS Region

**Data Type**: `String`

**Required**: `false`

### deploy

Create or update SSM paramaters and secrets in AWS Account.

``` shell
aws-secrets deploy
  --env-file 
  [--profile]
  [--region]
```

### Options

**Parameter**: `--env-file` or `-e`

**Description**: Environment file path

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--profile`

**Description**: AWS Profile

**Data Type**: `String`

**Required**: `false`

---

**Parameter**: `--region`

**Description**: AWS Region

**Data Type**: `String`

**Required**: `false`

### migrate

Clone an environment to another, used for change KMS Key as well.

``` shell
aws-secrets migrate
  --source
  --target
  --source-profile
  --source-region
  --target-profile
  --target-region
```

### Options

**Parameter**: `--source`

**Description**: Source environment file path

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--target`

**Description**: Target environment file path, this file must already be created and with `kms` there.

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--source-profile`

**Description**: Source AWS Profile

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--source-region`

**Description**: Source AWS Region

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--target-profile`

**Description**: Target AWS Profile

**Data Type**: `String`

**Required**: `true`

---

**Parameter**: `--target-region`

**Description**: Target AWS Region

**Data Type**: `String`

**Required**: `true`

### Resolvers

This CLI implements resolvers, which can be used to resolve value of a comand output or a CloudFormation output value.

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
> If you use `!cmd` resolver with `SecureString` you must disable decrypt action on deploy, otherwise the CLI will try to decrypt the resolved value and the process will be failed.
