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

This will compile the C/C++ parts of the module and create the python packages in the .egg and .wheel format
in the dist/ dir.

Installation
------------
You can install the module in the in the following ways:

To install the extension module system wide or into a venv:

``make install``

To install the extension module into you home dir:

``make install-user``


Virtualenv
----------
We recommend using a venv to work on/with the pEpPythonAdapter.
There is a convenience make target that will create and activate a venv that already has the LD_LIBRARY_PATH
or DYLD_LIBRARY_PATH set according to your ```local.conf``.
If the venv is not existing yet it will be created and activated.
If the venv already exists it will only be activated.

``make venv``

After that, to install the pEp module into the venv, do:

``make install``

Test
----
To run the whole testsuite you need to create/activate the venv, and then invoke the make target 'test'.
You can do this from a clean clone of the repo, no prior actions required, the whole module and all dependencies
will be compiled and installed into the venv.

``make venv``
``make test``


Module Development
------------------
To develop on the module itself, first of all create and activate a venv:

``make venv``

Then, in the venv install the module in development mode.

``make develop``

While developing there are two levels of changes. Changes to the python part of the module (pEp), and
changes to the C/C++ part of the module (_pEp). If you change just python code, the changes are effective immediately.
If you do changes to the C/C++ part you need to issue ``make develop`` again, to recompile the extension and install
the new binary (.so/.dylib) of the module into the venv.


Docker
------
If you know how to use docker, you can avoid having to install all
the dependencies using the image
https://registry.gitlab.com/juga0/pepdocker/peppythonadapter.

.. Note:: This docker image is not officially maintained and it exists only
   until there is an official Debian one.
