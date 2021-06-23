# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

"""Blob unit tests."""

import pytest

from . import constants
from . import model

def test_blob_data_constructor(pEp, model):
    bdata = bytes('this is test data', 'utf-8')
    b = pEp.Blob(bdata)
    assert(b.data == bdata)

def test_blob_data_property(pEp, model):
    b = pEp.Blob(b'dummy')
    bdata = bytes('this is test data', 'utf-8')
    b.data = bdata
    assert(b.data == bdata)
