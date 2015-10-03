# -*- coding: utf-8 -*-

"""Test testing functions."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op

from pytest import raises

from ..ast import AST
from ..testing import (ae, get_test_file_path, open_test_file,
                       iter_test_files, test_names, _test_readers)


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_ae():
    ae(1, 1)
    ae(1., 1)

    ae({'a': 1, 'm': {}}, {'a': 1})
    with raises(AssertionError):
        ae({'a': 1, 'b': {}}, {'a': 1})

    ae('abc\n', 'abc\n')
    with raises(AssertionError):
        ae('abc\n', 'abc')


def test_get_test_file_path():
    assert op.exists(get_test_file_path('hello_ast.py'))


def test_open_test_file():
    assert isinstance(open_test_file('hello_ast.py'), AST)
    with raises(ValueError):
        open_test_file('hello.idontexist')


def test_test_names():
    assert 'hello' in test_names()


def test_iter_test_files():
    tests = [(plugin_name, test_name)
             for (plugin_name, test_name, _) in iter_test_files()]
    assert ('json', 'hello') in tests


def test_test_readers():
    """Test the test file reader on a single test file."""
    plugin_name, test_name, path = next(iter_test_files())
    _test_readers(plugin_name, test_name, path)
