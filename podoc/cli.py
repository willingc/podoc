# -*- coding: utf-8 -*-

"""CLI tool."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import logging
import sys

import click

from podoc import __version__

logger = logging.getLogger(__name__)


#------------------------------------------------------------------------------
# CLI
#------------------------------------------------------------------------------

@click.command()
@click.argument('files', nargs=-1,
                type=click.Path(exists=True, file_okay=True,
                                dir_okay=True, resolve_path=True))
@click.option('-f', '-r', '--from', '--read')
@click.option('-t', '-w', '--to', '--write')
@click.option('-o', '--output')
@click.option('--data-dir')
@click.version_option(__version__)
@click.help_option()
def podoc(files=None, read=None, write=None, output=None, data_dir=None):
    """Convert one or several files from a supported format to another."""
    contents = ''.join(sys.stdin.readlines())
    print(contents)


if __name__ == '__main__':  # pragma: no cover
    podoc()
