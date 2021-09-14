# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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
