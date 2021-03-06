# -*- coding: utf-8 -*-

"""Test plugin system."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import os.path as op

from ..plugin import (IPluginRegistry, IPlugin, discover_plugins,
                      # _load_all_native_plugins,
                      get_plugin, get_plugins)
from ..utils import dump_text

from pytest import yield_fixture, raises


#------------------------------------------------------------------------------
# Fixtures
#------------------------------------------------------------------------------

@yield_fixture
def no_native_plugins():
    # Save the plugins.
    plugins = IPluginRegistry.plugins
    IPluginRegistry.plugins = []
    yield
    IPluginRegistry.plugins = plugins


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_plugins():
    from podoc.ast import ASTPlugin
    assert ASTPlugin in get_plugins()


def test_plugin_registration(no_native_plugins):
    class MyPlugin(IPlugin):
        pass

    assert IPluginRegistry.plugins == [MyPlugin]
    assert get_plugin('myplugin') == MyPlugin

    with raises(ValueError):
        get_plugin('unknown')


def test_discover_plugins(tempdir, no_native_plugins):
    path = op.join(tempdir, 'my_plugin.py')
    contents = '''from podoc import IPlugin\nclass MyPlugin(IPlugin): pass'''
    dump_text(contents, path)
    plugins = discover_plugins([tempdir])
    assert plugins
    assert plugins[0].__name__ == 'MyPlugin'
