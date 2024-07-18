# CHANGELOG

## v2.6.0 (2024-07-18)

### Feature

* feat: add `--show-diff` to deploy command (#62) ([`ed39eed`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/ed39eeda299799c051e0c8138092aed015d45c11))

## v2.5.0 (2024-07-17)

### Chore

* chore(release): 2.5.0 [skip ci] ([`c60545d`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/c60545d4920859b651cb5f73515596e7bf84a339))

### Ci

* ci: fix github actions lint workflow ([`5780ce9`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/5780ce9eac6c734ce719a4b9271427b7f4a3ce8c))

* ci: migrate github actions to python 3.9 ([`3cdf876`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/3cdf876bfa7066b8ff1ac97be5e452ec3df3f93e))

### Feature

* feat: improve set-parameter and set-secret commands (#61) ([`da74b79`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/da74b79518cf9a476013475119dfc95baa9f8cc3))

## v2.4.1 (2023-09-06)

### Chore

* chore(release): 2.4.1 [skip ci] ([`ec9a89e`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/ec9a89ea546e8bdecade80fbaf0a2fe05c721fea))

### Ci

* ci: add pypi publish github action step ([`5a638b8`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/5a638b891dc2b4fd9766805f612fe0df892a0364))

### Fix

* fix: Correct session import on output_stack.py (#59)

Co-authored-by: plinio.menarin &lt;menarin.plinio@ebanx.com&gt; ([`75ad28a`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/75ad28aec49a30dc5aabf187f6e9926b8ae8d0c3))

## v2.4.0 (2023-09-06)

### Chore

* chore(release): 2.4.0 [skip ci] ([`e9296d7`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/e9296d7e695242fd1a94d3ca074bde93dc0d2299))

### Ci

* ci: split release workflow ([`b9ab2f8`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/b9ab2f8992c2ba08e796da18511241ca2478f641))

* ci: remove github actions permissions section ([`9105c32`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/9105c32909d3c9d07bf40eb3118ca2f90426c546))

### Feature

* feat: add semantic release ([`d5f282e`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/d5f282ef8bebd35d0fb5e6b6f434b1456e8e0f18))

## v2.3.0 (2023-09-05)

### Ci

* ci(github-actions): split sonar workflow (#58)

* ci(github-actions): split sonar workflow

* remove unit tests spaces

* rollback spaces

* remove sonarcloud scan ([`90680a6`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/90680a6afa97b378ccf2a0f5aa59c5acdb2d1af4))

* ci: replace coverage reports to sonarcloud (#57)

* ci: replace coverage reports to sonarcloud

* move properties from sonarcloud properties to sonar-project

* test: coverage tests

* testing with coverage-reports

* use .coverage-reports

* rename sonar.python.coverage.reportPath property

* testing list coverage folder

* upgrade dev deps

* upgrade dev deps

* testing different coverage path format

* add relative_files flag

* rollback changes ([`60f41c8`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/60f41c8576d1f11116512b0f3d245c83a0420d61))

### Unknown

* release 2.3.0 ([`6c0faa9`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/6c0faa91a5afee7cf279a6d956b18f3750cd505d))

* Add region to `!cf_output` tag (#56)

Co-authored-by: plinio.menarin &lt;menarin.plinio@ebanx.com&gt; ([`058b374`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/058b374bf8b52d58beaff605bfd6c09b63baa070))

## v2.2.0 (2023-08-21)

### Unknown

* Release 2.2.0 ([`2732a3e`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/2732a3eece63efa426853f565e6388b8e85b271e))

* Fix issue with PyYaml and Cython (#51)

* Fix issue with PyYaml and Cython

* add required changes

---------

Co-authored-by: plinio.menarin &lt;menarin.plinio@ebanx.com&gt; ([`eaa0acc`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/eaa0acc25885468dbd62e0016074f8d699469616))

* Update Poetry version to `1.5.1` (#53)

* Update Poetry version to `1.5.1`

* set yaml formatter to prettier

---------

Co-authored-by: plinio.menarin &lt;menarin.plinio@ebanx.com&gt; ([`d0feccc`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/d0feccc4f3e0b62581821c26ffd1b674e1b83e59))

* Fix SonarCloud Code Smells (#47) ([`2a546f7`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/2a546f79ef80a28f343c9e93ceef7594a9b0393e))

## v2.1.0 (2022-05-23)

### Documentation

* docs: fix ([`fc02b86`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/fc02b860b19dff0097dfdd36376c5cbebc0ce37c))

### Feature

* feat(cli): add literal string style for multiline values ([`54e002a`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/54e002a8f7311940c23a06f103154bba23c001ee))

* feat(cli): replace argparse to click and create 2 new commands (decrypt and encrypt) ([`0503d5e`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/0503d5ee9ec31d947a62f00f70f8c73c1c5c0dc6))

* feat(cli): add support for tags ([`a465bda`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/a465bdae35bdc565b2a7b6037b5f119e9b2235f3))

* feat(cli): add support to use kms on parameters and secrets ([`7b58328`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/7b58328ee23d77895903978d7a1719d7387fbd47))

* feat(cli): get secret value from prompt insted of cli parameter ([`580000c`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/580000ca5d0497a78f9a26ed3de2ff64f235d5be))

### Fix

* fix(cli): optional profile or region ([`c0d2810`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/c0d281088487c0a85f43a7af9726d17753cb5e51))

* fix: check if secrets and parameters properties exists before deploy ([`f193133`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/f193133c6b254a3aa687387105be081bb23d24db))

* fix: create array when the property not exist ([`636cef8`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/636cef8b7e4a713c7f52dbe754c9ac173a448087))

* fix: github url ([`fcabb8b`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/fcabb8bde0263f98d382d4b6956db0e78c645656))

* fix: help command
docs: add more informations about CLI and resolvers ([`0034f85`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/0034f85ca49f69e611c82dd80ece34ff849415cf))

### Unknown

* [#28] Add support for more than 4kb encryption (#46) ([`b29d073`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/b29d0738d31aabac38e45848452996ef6d4274cb))

* Add `tier` property in the SSM parameter section #27 (#45) ([`8617790`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/861779099dd5a77c7166d69cad90bba5a1145001))

* Add Schema Validation for the SSM Parameters and Secrets Manager #42 (#44) ([`c38538d`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/c38538d1c5f60b2c89f2ddf9452f160c83bb6bac))

* [#34] Migrate the project structure to use Poetry (#43) ([`2b1e74a`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/2b1e74adc2f0d18466caeaffb00af0d93678d00b))

* [#40] Fix `!file` resolver, the path is not being resolved correctly based on the config directory (#41) ([`bede46c`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/bede46c70b1d175af97ed40ee4cd1f3bb77278a2))

* [#38] Fix `aws-secrets` commands, secrets file is not being loaded when the CLI is executed in a different folder (#39) ([`eaad2d8`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/eaad2d8a1f3d2848a943fff11734ddc3f9cfe9c4))

* Release v2.0.1 (#37) ([`614f3ef`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/614f3efd94bc4b31629d52f36c7454098b623d2a))

* [#35] Fix `aws-secrets deploy` CLI, the value changes always being detected when use YAML resolver (#36) ([`417d99c`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/417d99ce24b7d83bed2143590be3800c1b3499d7))

* Release v2.0.0 (#33) ([`68d3aad`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/68d3aadd7a2601f0e502b47a086983e202befc39))

* [#26] Add `!file` YAML resolver (#32) ([`e0689e2`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/e0689e2546c35b38b0642863305217dca0340105))

* [#25] Store the Ciphertext in a separate file (#31) ([`72d7b23`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/72d7b2309c3703d0d3c7cb18ded3cd0ddca46dd8))

* [#23] Add `aws` provider and add support for provider default value (#24) ([`3465eed`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/3465eed8f729dfa28c6280215bed95cc04ac800a))

* Releases `1.1.0` (#22) ([`85735fd`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/85735fd4cc0ad406eccc6007382e914446f9b7cc))

* [#16] Add `-d/--description` to the `set-parameter` and `set-secret` CLIs (#21) ([`4fe6b28`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/4fe6b2849639c167c6dbb8b51e25289b92454d1a))

* [#17] Fix the `deploy` CLI to the secrets without `--confirm` option (#20) ([`6ccec2b`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/6ccec2b9c5f2730398c875555c377fc9eeafd1aa))

* [#18] Fix the `deploy` CLI to the deploy new parameters with tags. (#19) ([`8d30bdc`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/8d30bdcae5bf6f33a87f8035aa8cd9234384cd54))

* [Issue 14] Add session provider for !cmd resolver (#15)

* [Issue 14] Add session provider for !cmd resolver

* update documentation

* fix docs

* fix the condition

* update beta version

* remove beta version ([`7593d34`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/7593d34c24d2123aec182dbf87d72907042ca689))

* Flake8 lint issues (#13) ([`5576a2a`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/5576a2abe87f199d95362f10e1f8dc017b7ab0c2))

* AWS secrets deploy dry-run and confirm click option (#12)

* #8 AWS secrets deploy dry-run and confirm click option

* Fixing SonarQube issues

* Fix SSM parameter Code Smell

* Fix SonarQube Issues

* Fix CodeSmell

* Add only-secrets and only-parameters

* Fix SonarQube Issues

* change version label

* Change version name

* Add filter-pattern and some bugfixes

* Fix SonarQube issues

* Fix documentation

* change version name ([`d22450d`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/d22450dcb4d280bd78fd115afa396472d9f4df0b))

* #6 - Fix resource tags (#11)

* #6 Fix - resource tags

* #3 format file ([`105c29f`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/105c29f3130739ed79f21543012ed6e2cbc8bcbe))

* #3 - Add version CLI command (#10)

* #3 - Add version CLI command

* #3 format files ([`53ed825`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/53ed8255e47ecefd817dc57638267633463ea865))

* Fix - issue #1 ([`78968a5`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/78968a5516ce24861186c966dccf9799615dfbdd))

* Fix Issue #1 (#9) ([`440c799`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/440c799f6185fd0ab9218fc0db2421d2c5dcaa23))

* Fix - Set-Parameter Command fails with &#39;NoneType&#39; (#5) ([`fb447fa`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/fb447fa33f1be68c7469f33adde02918b828ce66))

* fix on decrypt command ([`d221d62`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/d221d623a84ca4a12f753fdc5d249c8603943d0b))

* remove migrate command ([`55d8ecb`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/55d8ecb2db3f0adce9e9ce3d7ef22f7535acf2d2))

* change same file flag to output file name ([`3772994`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/37729948fc3156c602733b60229549489879f640))

* fix ([`719ce8e`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/719ce8e55ef0f85e31a801fc12e3f212c9206d0e))

* remove sonar project properties ([`01428d0`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/01428d095edd4b4cc5884cb4cd92c016b64eb0dc))

* fix organization key ([`61322be`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/61322be136c245d80dc132a571391df78953c71e))

* add github token environment variable ([`ca9eccb`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/ca9eccb0fd309cdd1b5e8c14bb7788aff1b9f1e4))

* remove multple python version ([`ac30bcb`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/ac30bcb57f24e339ca48a3e8605c8e7e794f82f4))

* add sonar project file ([`e7a3be1`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/e7a3be194f46ba459b0c2143652dd776cbed53b7))

* add sonar ([`a6954f3`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/a6954f3e756800c479214833184646405edae1df))

* initial version ([`6fb0bd3`](https://github.com/lucasvieirasilva/aws-ssm-secrets-cli/commit/6fb0bd3cc9b6d1ff67876b239698768f16c97678))
