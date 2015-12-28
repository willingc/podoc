# -*- coding: utf-8 -*-

"""Test core functionality."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op

from pytest import raises

from ..core import Podoc, _find_path, _get_annotation


#------------------------------------------------------------------------------
# Tests utils
#------------------------------------------------------------------------------

def test_get_annotation():
    assert _get_annotation(lambda: None, 'a') is None


def test_find_path():
    assert _find_path([(1, 2), (2, 3)], 1, 2) == [1, 2]
    assert _find_path([(1, 2), (2, 3)], 1, 3) == [1, 2, 3]
    assert _find_path([(1, 2), (2, 3), (1, 4), (4, 5)], 1, 5) == [1, 4, 5]


#------------------------------------------------------------------------------
# Tests podoc
#------------------------------------------------------------------------------

def test_podoc_fail():
    p = Podoc()
    with raises(ValueError):
        p.convert('hello', ['a', 'b'])


def test_podoc_1():
    p = Podoc()

    p.register_lang('lower')
    p.register_lang('upper')

    @p.register_func(source='lower', target='upper')
    def toupper(text):
        return text.upper()

    assert p.conversion_pairs == [('lower', 'upper')]
    assert p.convert('hello', ['lower', 'upper']) == 'HELLO'


def test_podoc_2():
    p = Podoc()

    p.register_lang('lower')
    p.register_lang('upper')

    @p.register_func(source='lower', target='upper')
    def toupper(text):
        return text.upper()

    @p.register_func(source='upper', target='lower')
    def tolower(text):
        return text.lower()

    assert p.convert('Hello', ['lower', 'upper', 'lower']) == 'hello'


def test_podoc_3(tempdir):
    p = Podoc()

    p.register_lang('a', file_ext='.a',
                    open_func=lambda path: 'a',
                    save_func=lambda path, contents: None,
                    )
    assert p.languages == ['a']

    assert p.get_lang_for_file_ext('.a') == 'a'
    assert p.get_lang_for_file_ext('.b') is None

    fn = op.join(tempdir, 'aa.a')
    open(fn, 'w').close()
    open(op.join(tempdir, 'bb.b'), 'w').close()

    with raises(AssertionError):
        p.get_files_in_dir('')
    assert p.get_files_in_dir(tempdir, lang='a') == [fn]
