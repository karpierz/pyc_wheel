pyc_wheel
=========

Compile all py files in a wheel to pyc files.

Overview
========

|package_bold| is a strict fork of Grant Patten's pycwheel_ package
with a fixes allowing to work with Python3 or higher and with a code
reformatting and some improvements.

`PyPI record`_.

`Documentation`_.

Usage
-----

Processing the wheel in place:

.. code-block:: bash

    $ python3 -m pyc_wheel your_wheel-1.0.0-py3-none-any.whl
    # Output: your_wheel-1.0.0-py3-none-any.whl

or renaming for the python version:

.. code-block:: bash

    $ python3.12 -m pyc_wheel --rename your_wheel-1.0.0-py3-none-any.whl
    # Output: your_wheel-1.0.0-cp312-none-any.whl

or with backup:

.. code-block:: bash

    $ python3.12 -m pyc_wheel --rename --with-backup your_wheel-1.0.0-py3-none-any.whl
    # Output: your_wheel-1.0.0-cp312-none-any.whl
    #         your_wheel-1.0.0-py3-none-any.whl.bak

or with quiet:

.. code-block:: bash

    $ python3 -m pyc_wheel --quiet your_wheel-1.0.0-py3-none-any.whl
    # Output: your_wheel-1.0.0-py3-none-any.whl

or skipping compilation for a file subset:

.. code-block:: bash

    $ python3 -m pyc_wheel --exclude "some/regex" your_wheel-1.0.0-py3-none-any.whl

To check all available processing options:

.. code-block:: bash

    $ python3 -m pyc_wheel --help

Installation
============

Prerequisites:

+ Python 3.10 or higher

  * https://www.python.org/

+ pip and setuptools

  * https://pypi.org/project/pip/
  * https://pypi.org/project/setuptools/

To install run:

  .. parsed-literal::

    python -m pip install --upgrade |package|

Development
===========

Prerequisites:

+ Development is strictly based on *tox*. To install it run::

    python -m pip install --upgrade tox

Visit `Development page`_.

Installation from sources:

clone the sources:

  .. parsed-literal::

    git clone |respository| |package|

and run:

  .. parsed-literal::

    python -m pip install ./|package|

or on development mode:

  .. parsed-literal::

    python -m pip install --editable ./|package|

License
=======

  | |copyright|
  | Copyright (c) 2016 Grant Patten
  | Licensed under the MIT License
  | https://opensource.org/license/mit
  | Please refer to the accompanying LICENSE file.

Authors
=======

* Grant Patten <grant@gpatten.com>
* Adam Karpierz <adam@karpierz.net>

.. |package| replace:: pyc_wheel
.. |package_bold| replace:: **pyc_wheel**
.. |copyright| replace:: Copyright (c) 2019-2025 Adam Karpierz
.. |respository| replace:: https://github.com/karpierz/pyc_wheel.git
.. _Development page: https://github.com/karpierz/pyc_wheel
.. _PyPI record: https://pypi.org/project/pyc_wheel/
.. _Documentation: https://pyc-wheel.readthedocs.io/
.. _pycwheel: https://pypi.org/project/pycwheel/
