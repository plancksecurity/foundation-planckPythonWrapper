# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

# from . import constants

import pathlib

def data_file_contents(name) -> str:
    """grab the contents of a file in the data folder"""
    path = pathlib.Path(__file__).parent / constants.DATADIR / name
    with path.open(mode='r') as fid:
        return fid.read()
