Installation
============

Requirements
------------
In order to build, use or install this extension module, you need to have some
system dependencies already installed:

* pEp-base (sequoia, libetpan, asn1c, yml2, pEpEngine, libpEpAdapter)
* boost-python

These `build instructions <https://dev.pep.foundation/Common%20Adapter%20Documentation/Adapter_Build_Instructions>`_ will get you all setup.

Additionally, there is a `build script <http://pep-security.lu/gitlab/juga/Internal-Deployment/-/blob/master/build-pep-stack.sh>`_
that executes these build instructions automatically (Debian and MacOS):

.. Note:: If you dont install pEp-base system wide, but under a prefix, like /home/foo/local/
   you will need to have LD_LIBARY_PATH/DYLD_LIBRARY_PATH adjusted for all the following operations.


Build
-----
The pEpPythonAdapter is a python extension module that contains C/C++ code that needs to be
compiled first. So, before any use or installation, the module needs to be built.

Build config
~~~~~~~~~~~~
Create a local build config by creating a 'local.conf' file. There is a 'local.conf.example' describing
all the build options. You can use this as a template.

``cp local.conf.example local.conf``


If you have pEp-base installed under a custom prefix (e.g. /home/foo/local) it is important
that you specify "PREFIX".

Build
~~~~~
To build the module just type:

``make``

Installation
------------
You can install this adapter in the in the following ways:

To install the extension module system wide or into a venv:

``make install``


To install the extension module into you home dir:

``make install-user``


If you're working on different Python projects, it's recommended to use
`virtualenv <https://virtualenv.pypa.io/en/stable/>`_ to have different
libraries versions.

If you're working in a virtualenv you can also install the package with
``pip install .``

To install the package in "develop mode", run ``python setup.py develop``
or ``pip install -e .``


Docker
------
If you know how to use docker, you can avoid having to install all
the dependencies using the image
https://registry.gitlab.com/juga0/pepdocker/peppythonadapter.

.. Note:: This docker image is not officially maintained and it exists only
   until there is an official Debian one.
