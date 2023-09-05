# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Changed

- Update yaml tag `tags.output_stack.OutputStackTag` to work with custom aws region. [issue-54](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/54)

## [2.2.0] - 2023-08-21

### Nonfunctional

- Update Poetry to version `1.5.1`. [issue-52](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/52)
- Fix SonarCloud Code Smells.

## [2.1.0] - 2022-05-23

### Added

- Add `Tier` property in the SSM parameter section. [issue-27](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/27)
- Add support for AWS Encription SDK. [issue-28](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/28)

### Changed

- Add Schema Validation for the SSM Parameters and Secrets Manager. [issue-42](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/42)

### Nonfunctional

- Migrate the project structure to use Poetry. [issue-34](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/34)

## [2.0.3] - 2021-09-14

### Fixed

- Fix `!file` resolver, the path is not being resolved correctly based on the config directory. [issue-40](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/40)

## [2.0.2] - 2021-09-14

### Fixed

- Fix `aws-secrets` commands, secrets file is not being loaded when the CLI is executed in a different folder. [issue-38](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/38)

## [2.0.1] - 2021-09-14

### Fixed

- Fix `aws-secrets deploy` CLI, the value changes always being detected when use YAML resolver. [issue-35](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/35)

## [2.0.0] - 2021-09-14

### Added

- Add `!file` YAML resolver. [issue-26](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/26)

### Changed

- Store the Ciphertext in a separate file. [issue-25](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/25)
- Add Global Catch Exception Handler to the CLI to avoid StackTrace messages. [issue-30](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/30)

#### BREAKING CHANGES

The changes in this PR are breaking changes.

The current version of the AWS Secrets CLI stores the values in the same config file and the new version look at another file.

Migration process:

To create the new `*.secrets.yaml` file, the AWS Secrets CLI needs to re-encrypt the config file.

```shell
aws-secrets decrypt -e <config-file> --output <decrypted-file>
```

```shell
aws-secrets encrypt -e <decrypted-file>
```

Remove the original file, rename the two new files to match with the original name, and modify the property `secrets_file` in the configuration YAML file.

## [1.2.0] - 2021-08-20

### Added

- Add `aws` provider in the `!cmd` YAML tag to resolve `--profile` and `--region` AWS CLI options. [issue-23](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/23)

### Changed

- Modify `!cmd` YAML tag to support default values for the provide resolvers. [issue-23](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/23)

## [1.1.0] - 2021-07-21

### Fixed

- Fix the `deploy` CLI to the deploy new parameters with tags. [issue-18](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/18)
- Fix the `deploy` CLI to the secrets without `--confirm` option. [issue-17](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/17)
- Add `-d/--description` to the `set-parameter` and `set-secret` CLIs. [issue-16](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/16)

## [1.0.1] - 2021-01-21

### Changed

- Add `session` resolver for `!cmd` resolver [issue-14](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/14)
