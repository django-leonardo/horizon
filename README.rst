=================
OpenStack Horizon
=================

This is not my code ! Why i created this package ? Because we need only Horizon without Openstack Dashboard dependencies !

Installing from git about 10min and 50Mb is past

**Now we have 527Kb on pypi ready to use anywhere !**

Plan for this repository is only follow main openstack project and propagate stable version of Horizon for us.

Now is there **stable/kilo** and development version from master, but we recommend using ``stable/kilo``


Horizon is a Django-based project aimed at providing a complete OpenStack
Dashboard along with an extensible framework for building new dashboards
from reusable components. The ``openstack_dashboard`` module is a reference
implementation of a Django site that uses the ``horizon`` app to provide
web-based interactions with the various OpenStack projects.

* Release management: https://launchpad.net/horizon
* Blueprints and feature specifications: https://blueprints.launchpad.net/horizon
* Issue tracking: https://bugs.launchpad.net/horizon


Using Horizon
=============

See ``doc/source/topics/install.rst`` about how to install Horizon
in your OpenStack setup. It describes the example steps and
has pointers for more detailed settings and configurations.

It is also available at http://docs.openstack.org/developer/horizon/topics/install.html.

Getting Started for Developers
==============================

``doc/source/quickstart.rst`` or
http://docs.openstack.org/developer/horizon/quickstart.html
describes how to setup Horizon development environment and start development.

Building Contributor Documentation
==================================

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source`` directory using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/

* Building Automatically::

    $ ./run_tests.sh --docs

* Building Manually::

    $ tools/with_venv.sh sphinx-build doc/source doc/build/html

Results are in the ``doc/build/html`` directory
