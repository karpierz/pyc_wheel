Changelog
=========

2.0.12 (2026-01-10)
-------------------
- Fixing the file exclusion error.
- Marked the package as typed.
- Copyright year update.
- The documentation has been moved from Read the Docs to GitHub Pages.
- Added the 'tool.tox.env.cleanup' test environment.
- Setup update (mainly dependencies) and bug fixes.

1.5.0 (2025-09-01)
------------------
- Made the package typed.
- Setup update (mainly dependencies).

1.3.6 (2025-07-07)
------------------
- Unittests have been added.
- 100% code coverage.
- A few minor code improvements.
- Setup update (mainly dependencies).

1.3.5 (2025-06-11)
------------------
- Setup update (mainly dependencies).

1.3.4 (2025-05-15)
------------------
- The distribution is now built using 'build' instead of 'setuptools'.
- Setup update (mainly dependencies) (due to regressions in tox and setuptools).

1.3.2 (2025-05-10)
------------------
- Added support for Python 3.14
- Dropped support for Python 3.9 (due to compatibility issues).
- Added support for PyPy 3.11
- Dropped support for PyPy 3.9
- `Add --rename and --symlink options.
  <https://github.com/karpierz/pyc_wheel/pull/20>`_
- `Fix for a bug <https://github.com/karpierz/pyc_wheel/issues/21>`_
- `Fix for a bug when wheel tag rewrite processed incorrectly
  <https://github.com/karpierz/pyc_wheel/issues/19>`_
- `Fix links in README.rst
  <https://github.com/karpierz/pyc_wheel/pull/15>`_
- Updated Read the Docs' Python version to 3.13
- Updated tox's base_python to version 3.13
- Setup update (mainly dependencies).

1.3.0 (2025-02-10)
------------------
- Added support for Python 3.10, 3.11, 3.12 and 3.13
- Dropped support for Python 3.6, 3.7 and 3.8
- Added support for PyPy 3.9 and 3.10
- `Add --optimize argument to allow setting the optimization level
  of the compiler. <https://github.com/karpierz/pyc_wheel/pull/14>`_
- `Wheel name should include Python tag.
  <https://github.com/karpierz/pyc_wheel/pull/13>`_
- `Preserve the permissions bits.
  <https://github.com/karpierz/pyc_wheel/pull/9>`_
- `Extend docs for --exclude and --help.
  <https://github.com/karpierz/pyc_wheel/pull/7>`_
- Add --log argument to allow logging.
- 100% code linting.
- Copyright year update.
- Setup update (currently based on pyproject.toml).
- | The tox configuration has been moved to pyproject.toml
  | and now based on tox >= 4.0
- Setup update (mainly dependencies).

1.2.7 (2021-10-14)
------------------
- Setup update.

1.2.6 (2021-07-20)
------------------
- Setup general update and improvement.

1.2.4 (2020-10-18)
------------------
- Dropped support for Python 3.5.
- Fixed docs setup.

1.1.0 (2020-09-22)
------------------
- Added support for Python 3.9.
- `Fixed improper permission setting to read distribution.
  <https://github.com/karpierz/pyc_wheel/pull/4>`_
- Setup general update and cleanup.

1.0.3 (2020-01-16)
------------------
- Added ReadTheDocs config file.
- Setup update.

1.0.2 (2019-12-03)
------------------
- Added the ability to exclude files from compilation.
- Added the ability to use wildcards.

1.0.1rc3 (2019-11-30)
---------------------
- A little fix for README.rst

1.0.1rc2 (2019-11-30)
---------------------
- | Creating a fork of Grant Patten's *pycwheel* package with a fixes,
  | changes and improvements allowing to work with Python3 or higher.

Changes of the original *pycwheel*:

1.0.0 (Sep 25, 2016)
--------------------
- Initial commit.
