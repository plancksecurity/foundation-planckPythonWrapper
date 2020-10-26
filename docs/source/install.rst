Installation
============

Requirements
------------

[Sequoia](https://gitlab.com/sequoia-pgp/sequoia)
[pEpEngine](https://pep.foundation/dev/repos/pEpEngine/)
[libpEpAdapter](https://pep.foundation/dev/repos/libpEpAdapter/)

## Build Instructions

To install all the dependencies, referer to their respective documentation.

These build instructions should work on:
 * Linux (Verified 26.4.20 - heck)
 * MacOS (Verified 26.4.20 - heck)
 * Windows

### Build
To build against system wide pEp installation (libs/includes)
```bash
python3 setup.py build_ext
```

To build against a pEp installation in your home dir (libs/includes):
```bash
python3 setup.py build_ext --local
```

To build against a pEp installation in a custom installation root (libs/includes)
```bash
python3 setup.py build_ext --prefix=<path_to_your_install_root>
```

Installation in all platforms
-----------------------------

It is possible to install `pEpPythonAdapter` without building it first, since
the installation process will build it when it has not been built yet, but you
need to have all the dependencies already installed.

You can install this adapter in the in the following ways:

To install the extension module system wide, as root, run:
```bash
python3 setup.py install
```

To install the extension module into you home dir
```bash
python3 setup.py install --user
```

To install the extension module into a custom destination
```bash
python3 setup.py install --prefix=<custom_destination_root>
```
Attention: The ~ (tilde) does not get expanded, but env vars work ($HOME).

If you're working on different Python projects, it's recommended to use
[virtualenv](https://virtualenv.pypa.io/en/stable/) to have different
libraries versions.

If you're working in a virtualenv you can also install the package with
`pip install .`

To install the package in "develop mode", run `python setup.py develop`
or `pip install -e .`

Debian installation
--------------------

You can also install the dependencies using the scripts
http://pep-security.lu/gitlab/juga/Internal-Deployment/-/blob/master/install-sys-deps-debian.sh
and
http://pep-security.lu/gitlab/juga/Internal-Deployment/-/blob/master/build-pep-stack.sh

If you know how to use docker, you can avoid having to install all
the dependencies using the image
https://registry.gitlab.com/juga0/pepdocker/peppythonadapter.

.. Note:: This docker image is not officially maintained and it exists only
   until there is an official Debian one.
