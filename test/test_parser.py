#! /usr/bin/env python
########################################################################
# SimpleFIX
# Copyright (C) 2016-2017, David Arnold.
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

import sys
import unittest

from simplefix import FixMessage, FixParser


def make_str(s):
    if sys.version_info.major == 2:
        return bytes(s)
    else:
        return bytes(s, 'ASCII')


class ParserTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        parser = FixParser()
        msg = parser.get_message()
        self.assertIsNone(msg)
        return

    def test_basic_fix_message(self):
        """Test parsing basic FIX message."""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_pair(29, "A")
        buf = pkt.encode()

        p = FixParser()
        p.append_buffer(buf)
        m = p.get_message()

        self.assertIsNotNone(m)
        self.assertEqual(b"FIX.4.2", m.get(8))
        self.assertEqual(b"D", m.get(35))
        self.assertEqual(b"A", m.get(29))
        return

    def test_parse_partial_string(self):
        """Test parsing incomplete FIX message."""
        parser = FixParser()
        parser.append_buffer("8=FIX.4.2\x019=")
        msg = parser.get_message()
        self.assertIsNone(msg)

        parser.append_buffer("5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)
        self.assertEqual(b"FIX.4.2", msg.get(8))
        self.assertEqual(b"5", msg.get(9))
        self.assertEqual(b"0", msg.get(35))
        self.assertEqual(b"161", msg.get(10))
        return

    def test_get_buffer(self):
        """Test reassembly of message fragments."""
        parser = FixParser()
        parser.append_buffer("8=FIX.4.2\x019=")
        msg = parser.get_message()
        self.assertIsNone(msg)

        buf = parser.get_buffer()
        self.assertEqual(b"9=", buf)

        parser.append_buffer("5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)

        buf = parser.get_buffer()
        self.assertEqual(b"", buf)
        return

    def test_leading_junk_pairs(self):
        """Test that leading junk pairs are ignored."""
        parser = FixParser()
        parser.append_buffer("1=2\x013=4\x018=FIX.4.2\x019=5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)
        self.assertIsNone(msg.get(1))
        self.assertIsNone(msg.get(3))
        return

    def test_junk_pairs(self):
        """Test that complete junk paris are ignored."""
        parser = FixParser()
        parser.append_buffer("1=2\x013=4\x015=6\x01")
        msg = parser.get_message()
        self.assertIsNone(msg)
        return

    def test_raw_data(self):
        """Test parsing of raw data fields."""
        raw = b"raw\x01data"

        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_data(95, 96, raw)
        buf = pkt.encode()

        parser = FixParser()
        parser.append_buffer(buf)
        msg = parser.get_message()

        self.assertIsNotNone(msg)
        self.assertEqual(b"FIX.4.2", msg.get(8))
        self.assertEqual(b"D", msg.get(35))
        self.assertEqual(len(raw), int(msg.get(95)))
        self.assertEqual(raw, msg.get(96))
        return

    def test_raw_data_tags(self):
        """Test functions to add and remove raw data tags."""
        raw = b"raw\x015000=1"

        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_data(5001, 5002, raw)
        buf = pkt.encode()

        parser = FixParser()
        parser.add_raw(5001, 5002)
        parser.append_buffer(buf)
        msg = parser.get_message()

        self.assertIsNotNone(msg)
        self.assertEqual(b"FIX.4.2", msg.get(8))
        self.assertEqual(b"D", msg.get(35))
        self.assertEqual(len(raw), int(msg.get(5001)))
        self.assertEqual(raw, msg.get(5002))

        parser.reset()
        parser.remove_raw(5001, 5002)
        parser.append_buffer(buf)
        msg = parser.get_message()

        self.assertIsNotNone(msg)
        self.assertEqual(b"FIX.4.2", msg.get(8))
        self.assertEqual(b"D", msg.get(35))
        self.assertEqual(len(raw), int(msg.get(5001)))
        self.assertEqual(b"raw", msg.get(5002))
        self.assertEqual(b"1", msg.get(5000))
        return


if __name__ == "__main__":
    unittest.main()
