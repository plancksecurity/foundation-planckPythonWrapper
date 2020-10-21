Testing
=======

See :ref:`install` to install the dependencies.

See `test/README.md` to run the tests in `test`.

To run the tests that use `pytest`, install the testing dependencies running
``pip install .[test]``.

In Debian, you can install the testing dependencies in the system running ``apt
install tox``.

Run the tests with the command `tox`. You can run individual tests by running
``tox -e <testname>``, eg. ``tox -e py37`` or ``tox -e unit``.
