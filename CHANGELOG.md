# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/) and this project
adheres to [Semantic Versioning](https://semver.org/). New entries are
generated from [Conventional Commits](https://www.conventionalcommits.org/)
by [multicz](https://github.com/goabonga/multicz).

## [1.1.1] - 2026-06-14

### Fixed

- **generate**: avoid IndexError when inputs have no optional variables (`ca794e5`)

## [1.1.0] - 2026-05-20

### Added

- support python-hcl2 8.x (`e85aacb`)

### Fixed

- **deps**: pin GitPython to 3.1.50 (`9e9b558`)

## [1.0.0] - 2026-05-20

### Breaking changes

- relicense from GPL-3.0 to MIT (`4c6cdce`)
- rename package to terragrunt_generator under src/ layout (`24f8104`)

## [0.17.1] - 2026-05-05

### Fixed

- re-publish 0.17.0 as 0.17.1

## [0.17.0] - 2025-04-27

### Added

- **cli**: support multiple --yaml-output and --yaml-for-env options

## [0.16.2] - 2025-04-25

### Fixed

- **yaml**: properly format multiline descriptions and default values

## [0.16.1] - 2025-04-24

### Fixed

- **yaml**: improve YAML merge logic with recursive block merging and header preservation

## [0.16.0] - 2025-04-24

### Added

- **cli**: improve help messages and CLI argument descriptions

## [0.15.0] - 2025-04-24

### Added

- add --enabled flag to CLI and propagate to YAML generation

## [0.14.1] - 2025-04-24

### Fixed

- improve merge_yaml_strings logic and output path resolution

## [0.14.0] - 2025-04-24

### Added

- support YAML config file per environment with --yaml-for-env

## [0.13.0] - 2025-04-24

### Added

- **cli**: allow overriding default config filename via CLI

## [0.12.0] - 2025-04-24

### Added

- **yaml**: add support for merging and writing YAML output to file

## [0.11.0] - 2025-04-24

### Added

- **generate**: return both HCL and YAML as tuple in generate and generate_header

## [0.10.0] - 2025-04-24

### Added

- **cli**: support output path with directory or filename

## [0.9.1] - 2025-04-24

### Fixed

- **generator**: use  for PEP8 compliance

## [0.9.0] - 2024-09-25

### Added

- bump all packages to the latest version

## [0.8.0] - 2024-09-15

### Added

- render nested yaml config based on lookup
- catch exception on copy_terraform_module
- make module optional into yaml config file

### Fixed

- E741 ambiguous variable name 'l'
- make lookup argument as required

## [0.7.6] - 2024-05-11

### Fixed

- using copytree from shutil

## [0.7.5] - 2024-01-20

### Fixed

- **deps**: bump gitpython from 3.1.35 to 3.1.41

## [0.7.4] - 2023-09-28

## [0.7.3] - 2023-09-19

### Fixed

- **sec**:  Known security vulnerabilities detected CVE-2023-40590

## [0.7.2] - 2023-08-04

### Fixed

- issues allowing parsing error and fix source path for local modules

## [0.7.1] - 2023-08-03

### Fixed

- cleaning up code and fix issues

## [0.7.0] - 2023-08-02

### Added

- apply best practices

## [0.6.6] - 2023-08-02

### Fixed

- **deps**: bump gitpython from 3.1.27 to 3.1.30

## [0.6.5] - 2023-08-01

### Fixed

- issues with generator for nullable inputs

## [0.6.4] - 2023-08-01

### Fixed

- lookup implementation should be neutral

## [0.6.3] - 2023-08-01

### Fixed

- issue issues with multiline descriptions

## [0.6.2] - 2023-04-08

### Fixed

- fix issues and apply good practices

## [0.6.1] - 2022-09-11

### Fixed

- remove scheme into terraform module path for  http(s)

## [0.6.0] - 2022-09-10

### Added

- add workflows :)

## [0.5.4] - 2022-09-10

### Fixed

- description error one nullable

## [0.5.3] - 2022-09-10

### Fixed

- builder

## [0.5.2] - 2022-09-10

### Fixed

- need a release note

## [0.5.1] - 2022-09-10

### Fixed

- check workflows

## [0.5.0] - 2022-09-10

### Added

- add changelog

### Fixed

- fix ci and workflows
- fix ci and workflows
- ci can publish release
- use vesrion tag name

## [0.4.0] - 2022-09-10

### Fixed

- use vesrion tag name

## [0.3.8] - 2022-09-10

### Fixed

- cleaning up ci remove unused configuration

## [0.3.7] - 2022-09-10

### Fixed

- make workflows great again

## [0.3.6] - 2022-09-10

### Fixed

- make workflows great again

## [0.3.5] - 2022-09-10

### Fixed

- make workflows great again

## [0.3.4] - 2022-09-10

### Fixed

- fixing workflow and configuration

## [0.3.3] - 2022-09-10

### Fixed

- fix ci workflows

## [0.3.1] - 2022-09-10

### Fixed

- let commitizen change poetry.tool version

## [0.3.0] - 2022-09-10

### Added

- install commitizen

## [0.2.1] - 2022-09-09

## [0.2.0] - 2022-09-09

## [0.1.0] - 2022-09-09
