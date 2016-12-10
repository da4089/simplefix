#! /usr/bin/env python
########################################################################
# SimpleFIX
# Copyright (C) 2016, David Arnold.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
########################################################################

import unittest
from simplefix import FixMessage, FixParser


class ParserTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_empty_string(self):
        parser = FixParser()
        msg = parser.get_message()
        self.assertIsNone(msg)
        return

    def test_basic_fix_message(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_pair(29, "A")
        buf = pkt.encode()

        p = FixParser()
        p.append_buffer(buf)
        m = p.get_message()

        self.assertIsNotNone(m)
        self.assertEqual("FIX.4.2", m.get(8))
        self.assertEqual("D", m.get(35))
        self.assertEqual("A", m.get(29))
        return

    def test_parse_partial_string(self):
        parser = FixParser()
        parser.append_buffer("8=FIX.4.2\x019=")
        msg = parser.get_message()
        self.assertIsNone(msg)

        parser.append_buffer("5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)
        self.assertEqual("FIX.4.2", msg.get(8))
        self.assertEqual("5", msg.get(9))
        self.assertEqual("0", msg.get(35))
        self.assertEqual("161", msg.get(10))
        return

    def test_get_buffer(self):
        parser = FixParser()
        parser.append_buffer("8=FIX.4.2\x019=")
        msg = parser.get_message()
        self.assertIsNone(msg)

        buf = parser.get_buffer()
        self.assertEqual("9=", buf)

        parser.append_buffer("5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)

        buf = parser.get_buffer()
        self.assertEqual("", buf)
        return

    def test_leading_junk_pairs(self):
        parser = FixParser()
        parser.append_buffer("1=2\x013=4\x018=FIX.4.2\x019=5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)
        self.assertIsNone(msg.get(1))
        self.assertIsNone(msg.get(3))
        return

    def test_junk_pairs(self):
        parser = FixParser()
        parser.append_buffer("1=2\x013=4\x015=6\x01")
        msg = parser.get_message()
        self.assertIsNone(msg)
        return


if __name__ == "__main__":
    unittest.main()
