# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Fixed

- Fix the `deploy` CLI to the deploy new parameters with tags. [issue-18](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/18)
- Fix the `deploy` CLI to the secrets without `--confirm` option. [issue-17](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/17)

## [1.0.1] - 2021-01-21

### Changed

- Add `session` resolver for `!cmd` resolver [issue-14](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/issues/14)