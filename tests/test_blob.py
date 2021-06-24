# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

"""Blob unit tests."""

import pytest

from . import constants
from . import model

def test_blob_data_constructor(pEp):
    bdata = b'this is binary \x00\x01\xbb\xa7\xa4\xab test data'
    b = pEp.Blob(bdata)
    assert b.data == bdata
    assert not b.mime_type
    assert not b.filename


def test_blob_data_property(pEp):
    bdata = b'this is binary \x00\x01\xbb\xa7\xa4\xab test data'
    b = pEp.Blob(b'dummy')
    b.data = bdata
    assert b.data == bdata
    assert not b.mime_type
    assert not b.filename


def test_blob_data_property_keeps_other_fields(pEp):
    bdata = b'this is binary \x00\x01\xbb\xa7\xa4\xab test data'
    b = pEp.Blob(b'dummy', 'application/x-mydata', 'myfile.dat')
    b.data = bdata
    assert b.data == bdata
    assert b.mime_type == 'application/x-mydata'
    assert b.filename == 'myfile.dat'
