"""Unit test for pEp package, not for subpackages or modules."""

from pEp import __version__


def test_pep_version():
    """    Test that __version__ is not None or empty and is not 0.0.0."""
    # We could also test that match the regex, but that is already a test in
    # setuptools_scm itself.
    assert __version__
    assert __version__ != "0.0.0"