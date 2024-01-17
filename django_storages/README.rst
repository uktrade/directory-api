.. image:: https://raw.githubusercontent.com/jschneier/django_storages/master/docs/logos/horizontal.png
    :alt: django_storages
    :width: 100%

.. image:: https://img.shields.io/pypi/v/django_storages.svg
    :target: https://pypi.org/project/django_storages/
    :alt: PyPI Version

.. image:: https://github.com/jschneier/django_storages/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/jschneier/django_storages/actions/workflows/ci.yml
    :alt: Build Status

Installation
============
Installing from PyPI is as easy as doing:

.. code-block:: bash

  pip install django_storages

If you'd prefer to install from source (maybe there is a bugfix in master that
hasn't been released yet) then the magic incantation you are looking for is:

.. code-block:: bash

  pip install -e 'git+https://github.com/jschneier/django_storages.git#egg=django_storages'

For detailed instructions on how to configure the backend of your choice please consult the documentation.

About
=====
django_storages is a project to provide a variety of storage backends in a single library.

This library is usually compatible with the currently supported versions of
Django. Check the Trove classifiers in setup.py to be sure.

django_storages is backed in part by `Tidelift`_. Check them out for all of your enterprise open source
software commercial support needs.

.. _Tidelift: https://tidelift.com/subscription/pkg/pypi-django_storages?utm_source=pypi-django_storages&utm_medium=referral&utm_campaign=enterprise&utm_term=repo

Security
========

To report a security vulnerability, please use the `Tidelift security contact`_. Tidelift will coordinate the
fix and disclosure. Please **do not** post a public issue on the tracker.

.. _Tidelift security contact: https://tidelift.com/security


Found a Bug?
============

Issues are tracked via GitHub issues at the `project issue page
<https://github.com/jschneier/django_storages/issues>`_.

Documentation
=============
Documentation for django_storages is located at https://django_storages.readthedocs.io/.

Contributing
============

#. `Check for open issues
   <https://github.com/jschneier/django_storages/issues>`_ at the project
   issue page or open a new issue to start a discussion about a feature or bug.
#. Fork the `django_storages repository on GitHub
   <https://github.com/jschneier/django_storages>`_ to start making changes.
#. Add a test case to show that the bug is fixed or the feature is implemented
   correctly.
#. Bug me until I can merge your pull request.

Please don't update the library version in CHANGELOG.rst or ``storages/__init__.py``, the maintainer will do that on release.
If you're the first to update the CHANGELOG in this release cycle, just put the version as ``XXXX-XX-XX``.

History
=======
This repo began as a fork of the original library under the package name of django_storages-redux and
became the official successor (releasing under django_storages on PyPI) in February of 2016.
