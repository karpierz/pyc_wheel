pyc_wheel
=========

*Compile all py files in a wheel to pyc files.*

Overview
========

  |package_bold| is a strict fork of Grant Patten's pycwheel_ package
  with a fixes allowing to work with Python3 or higher and with a code
  reformatting and some improvements.

Usage
-----

Processing the wheel in place:

.. code-block:: bash

    $ python -m pyc_wheel your_wheel-1.0.0-py3-none-any.whl
    # Output: your_wheel-1.0.0-py3-none-any.whl

or with backup:

.. code-block:: bash

    $ python -m pyc_wheel your_wheel-1.0.0-py3-none-any.whl --with_backup
    # Output: your_wheel-1.0.0-py3-none-any.whl
    #         your_wheel-1.0.0-py3-none-any.whl.bak

or with quiet:

.. code-block:: bash

    $ python -m pyc_wheel your_wheel-1.0.0-py3-none-any.whl --quiet
    # Output: your_wheel-1.0.0-py3-none-any.whl

Installation
============

Prerequisites:

+ Python 3.5 or higher

  * https://www.python.org/
  * 3.7 is a primary test environment.

+ pip and setuptools

  * https://pypi.org/project/pip/
  * https://pypi.org/project/setuptools/

To install run:

.. parsed-literal::

    python -m pip install --upgrade |package|

Development
===========

Visit `development page`_.

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

Prerequisites:

+ Development is strictly based on *tox*. To install it run::

    python -m pip install --upgrade tox

License
=======

  | Copyright (c) 2016 Grant Patten
  | Copyright (c) 2019-2019 Adam Karpierz
  |
  | Licensed under the MIT License
  | https://opensource.org/licenses/MIT
  | Please refer to the accompanying LICENSE file.

Authors
=======

* Grant Patten <grant@gpatten.com>
* Adam Karpierz <adam@karpierz.net>

.. |package| replace:: pyc_wheel
.. |package_bold| replace:: **pyc_wheel**
.. |respository| replace:: https://github.com/karpierz/pyc_wheel.git
.. _development page: https://github.com/karpierz/pyc_wheel/

.. _pycwheel: https://pypi.org/project/pycwheel/
