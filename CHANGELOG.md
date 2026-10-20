# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

We use the following:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [unreleased]

## [0.7.3]

### Added

- `download_verified(url, file_name, known_hash)` downloads a file into the cache of the solution if it is not there,
  as `download_if_not_exists` does, and checks its content against a hash written as in the resource file of a
  solution, e.g. `"sha256:<hex digest>"`: a file in the cache with another content is downloaded again, a download
  with another content is removed and raises a `ValueError` (!19, album#265). It needs no other package.
- Arguments can have the type `str`, `int` or `bool`, the Python names of `string`, `integer` and `boolean`
  (album#240). A solution that uses them needs `album_api_version` 0.7.3 or newer: older versions pass the value on
  as text.

### Changed

- Python 3.14 is listed among the supported Python versions; the CI tests it
- An argument with an unknown type stops the solution with a `ValueError` that names the argument and the type,
  instead of passing its value on as text (album#240)
- CI: a merge into main starts the release jobs only if it changes `pyproject.toml`, as in the other album
  repositories
- CI: `prepare release` stops with a message while the group variable `ALBUM_DEV_ENVIRONMENTS` is on, so a
  merge into main during the preparations of a release publishes nothing

### Fixed

- `album test`: the arguments of the test goal are parsed before `pre_test()` runs, so a required argument cannot be
  supplied by `pre_test()` (!16, album#171)
- `get_resources_dict()`: the docstring describes `os_specific` inverted and does not say what the dictionary holds (!17)

## [0.7.2]

### Changed

- the CI sets up Python with a newer micromamba version

### Fixed

- mypy issues (!14)

## [0.7.1]

### Changed

- project.toml over setup.cfg

### Added

- reconstruct changelog
- changelog to the repository

[unreleased]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.7.3...HEAD
[0.7.3]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.7.2...v0.7.3
[0.7.2]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.7.1...v0.7.2
[0.7.1]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.7.0...v0.7.1
[0.7.0]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.6.1...v0.7.0
[0.6.1]: https://gitlab.com/album-app/album-solution-api/-/compare/v0.6.0...v0.6.1
[0.6.0]: https://gitlab.com/album-app/album-solution-api/-/tags/v0.6.0
