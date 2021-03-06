# -*- coding: utf-8 -*-

"""Test Markdown plugin."""


#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import json

from pytest import fixture
from CommonMark import Parser
from six import string_types

from podoc.ast import ASTNode, ast_from_pandoc
from podoc.utils import pandoc, PANDOC_MARKDOWN_FORMAT
from .._markdown import (CommonMarkToAST, ASTToMarkdown, MarkdownPlugin)


#------------------------------------------------------------------------------
# Fixtures
#------------------------------------------------------------------------------

@fixture
def commonmark():
    contents = 'hello *world*'
    parser = Parser()
    cm = parser.parse(contents)
    return cm


@fixture
def ast():
    # TODO: move this to conftest
    ast = ASTNode('root')

    # First block
    block = ASTNode(name='Para',
                    children=['hello '])
    inline = ASTNode(name='Emph')
    inline.add_child('world')
    block.add_child(inline)
    ast.add_child(block)
    return ast


@fixture
def markdown():
    return 'hello *world*'


#------------------------------------------------------------------------------
# Test CommonMark to AST
#------------------------------------------------------------------------------

def test_cm_to_ast(commonmark, ast):
    ast_t = CommonMarkToAST().transform_main(commonmark)
    ast.show()
    ast_t.show()
    assert ast == ast_t


#------------------------------------------------------------------------------
# Test AST to Markdown
#------------------------------------------------------------------------------

def test_ast_to_markdown(ast, markdown):
    md = ASTToMarkdown().transform(ast)
    assert md == markdown


#------------------------------------------------------------------------------
# Test Markdown plugin
#------------------------------------------------------------------------------

def test_markdown_read(ast, markdown):
    assert MarkdownPlugin().read(markdown) == ast


def test_markdown_write(ast, markdown):
    assert MarkdownPlugin().write(ast) == markdown


# -----------------------------------------------------------------------------
# Test Markdown renderer inline
# Check safe round-tripping on CommonMark -> AST -> CommonMark
# -----------------------------------------------------------------------------

def _tree_contains_nodes(ast, names):
    if isinstance(ast, string_types):
        return False
    if ast.name in names:
        return True
    return all(any(_tree_contains_nodes(child, (name,))
                   for child in ast.children)
               for name in names)


def _test_renderer(s, *contains_nodes):
    """Test the renderer on a string."""
    # Parse the string with CommonMark-py.
    ast = MarkdownPlugin().read(s)
    print()
    print('****** PODOC AST ******')
    ast.show()
    # Check that the tree contains a node.
    if contains_nodes:
        assert _tree_contains_nodes(ast, contains_nodes)

    # Check markdown =(podoc)=> AST =(podoc)=> markdown.
    contents = ASTToMarkdown().transform(ast)
    assert contents.strip() == s

    # Check markdown =(podoc)=> AST =(pandoc)=> markdown.
    pandoc_json = json.dumps(ast.to_pandoc(), indent=2)
    markdown_pandoc = pandoc(pandoc_json,
                             PANDOC_MARKDOWN_FORMAT, format='json')
    # NOTE: the pandoc-converted Markdown is not guaranteed to
    # be equal to the original Markdown document. For example * List
    # is transformed into - List, same with ATXHeader etc.
    # However, we do test that the generated JSON is compatible with pandoc.
    assert markdown_pandoc

    # Check markdown_pandoc =(podoc)=> (AST_pandoc == AST_podoc).
    ast_0 = MarkdownPlugin().read(markdown_pandoc)
    print('****** PODOC AST (from markdown_pandoc) ******')
    ast_0.show()
    assert ast_0 == ast

    # Check markdown =(pandoc)=> (AST_pandoc == AST_podoc).
    p = pandoc(s, 'json', format=PANDOC_MARKDOWN_FORMAT)
    # NOTE: we use the '-' bullet char in the tests, for better compatibility
    # with pandoc.
    ast_1 = ast_from_pandoc(json.loads(p),
                            bullet_char='-')
    print('****** PODOC AST (via pandoc) ******')
    ast_1.show()
    assert ast_1 == ast


def test_markdown_renderer_simple():
    _test_renderer('hello')
    _test_renderer('hello world')
    _test_renderer('hello *world*', 'Emph')
    _test_renderer('hello **world**', 'Strong')


def test_markdown_renderer_link():
    _test_renderer('[hello](world)', 'Link')
    _test_renderer('![hello](world)', 'Image')


def test_markdown_renderer_codeinline():
    _test_renderer('hello `world`', 'Code')


# -----------------------------------------------------------------------------
# Test Markdown renderer block
# -----------------------------------------------------------------------------

def test_markdown_renderer_header():
    _test_renderer('# Hello', 'Header')
    _test_renderer('## Hello world', 'Header')


def test_markdown_renderer_codeblock():
    _test_renderer('```\nhello world\n```', 'CodeBlock')
    _test_renderer('```python\nhello world\n```', 'CodeBlock')


def test_markdown_renderer_blockquote():
    _test_renderer('> hello world', 'BlockQuote')
    _test_renderer('> hello world\n> end', 'BlockQuote')


def test_markdown_renderer_bullet_list():
    _test_renderer('- Item 1')
    _test_renderer('- Item 1\n- Item 2')
    # TODO: fix the following test
    # _test_renderer('- Item 1\n  - Item 1.2')


def test_markdown_renderer_ordered_list():
    _test_renderer('1. Item 1')
    _test_renderer('1. Item 1\n2. Item 2')
    _test_renderer('2. Item 1\n3. Item 2')


# -----------------------------------------------------------------------------
# Test Markdown renderer multiple blocks
# -----------------------------------------------------------------------------

def test_markdown_renderer_paras():
    _test_renderer('hello\nworld')
    _test_renderer('hello\n\nworld')


def test_markdown_renderer_headers():
    _test_renderer('# 1\n\n# 2')
    _test_renderer('# 1\n\n## 2')
    _test_renderer('## 2\n\n# 1')


def test_markdown_renderer_codeblocks():
    _test_renderer('```python\nhello world\n```\n\n```\nother\n```')


def test_markdown_renderer_ordered_bullet():
    # NOTE: we use `-` bullets instead of `*` to ensure stable round-trip
    # with pandoc which uses - by default.
    _test_renderer('1. Item 1\n\n- Bullet',
                   'BulletList', 'OrderedList')
    _test_renderer('- Bullet\n\n1. Item 1',
                   'BulletList', 'OrderedList')
    _test_renderer('1. Item 1\n2. Item 2\n\n- Bullet',
                   'BulletList', 'OrderedList')
    _test_renderer('1. Item 1\n2. Item 2\n\n- Bullet\n\n3. Item 3',
                   'BulletList', 'OrderedList')


def test_markdown_math_inline():
    _test_renderer('a $x*x=y*y$ b', 'Math')


def test_markdown_math_block():
    _test_renderer(r'$$\int_a^b f_0(x) dx$$', 'MathBlock')
    _test_renderer(r'$$\begin{eqnarray}\nx &= y\n\end{eqnarray}$$',
                   'MathBlock')
