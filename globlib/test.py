# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/09/22
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, re

import globlib

#------------------------------------------------------------------------------
class TestGloblib(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_tokenizer(self):
    self.assertEqual(
      list(globlib.Tokenizer('/foo/bar').tokens()),
      [('literal', '/foo/bar', 0, 8)])
    self.assertEqual(
      list(globlib.Tokenizer('/foo\/bar').tokens()),
      [('literal', '/foo/bar', 0, 9)])
    self.assertEqual(
      list(globlib.Tokenizer('/foo/*/bar').tokens()),
      [('literal', '/foo/', 0, 5),
       ('multiple', '*', 5, 6),
       ('literal', '/bar', 6, 10),
       ])
    self.assertEqual(
      list(globlib.Tokenizer('/foo/**/bar/*.txt').tokens()),
      [('literal', '/foo/', 0, 5),
       ('any', '**', 5, 7),
       ('literal', '/bar/', 7, 12),
       ('multiple', '*', 12, 13),
       ('literal', '.txt', 13, 17),
       ])
    self.assertEqual(
      list(globlib.Tokenizer('/foo/??.txt').tokens()),
      [('literal', '/foo/', 0, 5),
       ('single', '?', 5, 6),
       ('single', '?', 6, 7),
       ('literal', '.txt', 7, 11),
       ])
    self.assertEqual(
      list(globlib.Tokenizer('/foo/??.txt').tokens()),
      [('literal', '/foo/', 0, 5),
       ('single', '?', 5, 6),
       ('single', '?', 6, 7),
       ('literal', '.txt', 7, 11),
       ])
    self.assertEqual(
      list(globlib.Tokenizer(r'/foo/?\?.txt').tokens()),
      [('literal', '/foo/', 0, 5),
       ('single', '?', 5, 6),
       ('literal', '?.txt', 6, 12),
       ])
    self.assertEqual(
      list(globlib.Tokenizer(r'/foo-[a-z0-9].txt').tokens()),
      [('literal', '/foo-', 0, 5),
       ('range', 'a-z0-9', 5, 13),
       ('literal', '.txt', 13, 17),
       ])
    self.assertEqual(
      list(globlib.Tokenizer(r'/foo-{\\D{2,4\}}.txt').tokens()),
      [('literal', '/foo-', 0, 5),
       ('regex', r'\D{2,4}', 5, 16),
       ('literal', '.txt', 16, 20),
       ])

  #----------------------------------------------------------------------------
  def test_iswild(self):
    self.assertTrue(globlib.iswild('/foo/bar/**.ini'))
    self.assertTrue(globlib.iswild('/foo/bar-[0-9].ini'))
    self.assertFalse(globlib.iswild('/foo/bar/conf.ini'))
    self.assertFalse(globlib.iswild(r'\/foo\/bar\/conf.ini'))

  #----------------------------------------------------------------------------
  def test_match(self):
    self.assertIsNotNone(globlib.match('/foo/bar/**.ini', '/foo/bar/conf.ini'))
    self.assertIsNotNone(globlib.match('/foo/bar/**.ini', '/foo/bar/a/b/c/conf.ini'))
    self.assertIsNone(globlib.match('/foo/bar/**.ini', '/a/foo/bar/conf.ini'))
    self.assertIsNone(globlib.match('/foo/bar/**.ini', '/foo/bar/conf.ini.txt'))
    self.assertIsNone(globlib.match('/foo/bar/**.ini', '/foo/bar/conf.ini/zig.txt'))
    self.assertIsNone(globlib.match('/foo/bar/**.ini', '/FOO/BAR/ZIP/CONF.INI'))
    self.assertIsNotNone(globlib.match('/foo/bar/**.ini', '/FOO/BAR/ZIP/CONF.INI', flags=re.IGNORECASE))

  #----------------------------------------------------------------------------
  def test_search(self):
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/foo/bar/conf.ini'))
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/foo/bar/a/b/c/conf.ini'))
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/a/foo/bar/conf.ini'))
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/foo/bar/conf.ini.txt'))
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/foo/bar/conf.ini/zig.txt'))
    self.assertIsNone(globlib.search('/foo/bar/**.ini', '/foo/bar/conf.txt'))
    self.assertIsNone(globlib.search('/foo/bar/**.ini', '/X/FOO/BAR/ZIP/CONF.INI'))
    self.assertIsNotNone(globlib.search('/foo/bar/**.ini', '/X/FOO/BAR/ZIP/CONF.INI', flags=re.IGNORECASE))

  #----------------------------------------------------------------------------
  def test_compile(self):
    expr = globlib.compile('/foo/bar/*.dir/**.ini', flags=0)
    self.assertEqual(expr.pattern, r'\/foo\/bar\/[^/]*?\.dir\/.*?\.ini')
    expr = globlib.compile('/foo/bar-??-[a-z0-9].ini', flags=0)
    self.assertEqual(expr.pattern, r'\/foo\/bar\-[^/][^/]\-[a-z0-9]\.ini')

  #----------------------------------------------------------------------------
  def test_compile_exact(self):
    expr = globlib.compile('/foo/bar/*.dir/**.ini', flags=globlib.EXACT)
    self.assertEqual(expr.pattern, r'^\/foo\/bar\/[^/]*?\.dir\/.*?\.ini$')
    self.assertIsNotNone(expr.match('/foo/bar/a.dir/blue/conf.ini'))
    self.assertIsNotNone(expr.match('/foo/bar/a.dir/conf.ini'))
    self.assertIsNone(expr.match('/foo/bar/blue/a.dir/conf.ini'))
    self.assertIsNone(expr.match('/foo/bar/a.dir/conf.ini.x'))
    self.assertIsNone(expr.match('/x/foo/bar/a.dir/conf.ini'))

  #----------------------------------------------------------------------------
  def test_prefix(self):
    self.assertEqual(globlib.compile('/foo/bar', split_prefix=True)[0], '/foo/bar')
    self.assertEqual(globlib.compile('/foo/b**', split_prefix=True)[0], '/foo/b')
    self.assertEqual(globlib.compile('??/foo/b**', split_prefix=True)[0], '')

  #----------------------------------------------------------------------------
  def test_complete(self):
    expr = globlib.compile(r'/foo[0-9a-f]/*/bar\[??\]/{\\D{2,4\}}/**.txt')
    self.assertEqual(
      expr.pattern,
      r'\/foo[0-9a-f]\/[^/]*?\/bar\[[^/][^/]\]\/\D{2,4}\/.*?\.txt')
    self.assertIsNotNone(expr.match('/foo6/zog/bar[16]/abra/cadabra.txt'))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------