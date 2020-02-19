#! /usr/bin/env python
########################################################################
# SimpleFIX
# Copyright (C) 2016-2020, David Arnold.
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

from simplefix import FixMessage, FixParser, SOH_STR


def make_str(s):
    if sys.version_info.major == 2:
        return bytes(s)
    else:
        return bytes(s, 'ASCII')


# Python 2.6's unittest.TestCase doesn't have assertIsNone()
def test_none(self, other):
    return True if other is None else False


# Python 2.6's unittest.TestCase doesn't have assertIsNotNone()
def test_not_none(self, other):
    return False if other is None else True


class ParserTests(unittest.TestCase):


    def setUp(self):
        if not hasattr(self, "assertIsNotNone"):
            ParserTests.assertIsNotNone = test_not_none
        if not hasattr(self, "assertIsNone"):
            ParserTests.assertIsNone = test_none
        return

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
        pkt.append_pair(20000, "private tag")
        buf = pkt.encode()

        parser = FixParser()
        parser.append_buffer(buf)
        msg = parser.get_message()

        self.assertIsNotNone(msg)
        self.assertEqual(b"FIX.4.2", msg.get(8))
        self.assertEqual(b"D", msg.get(35))
        self.assertEqual(len(raw), int(msg.get(95)))
        self.assertEqual(raw, msg.get(96))
        self.assertEqual(b"private tag", msg.get(20000))
        return

    def test_raw_data_tags(self):
        """Test functions to add and remove raw data tags."""
        raw = b"raw\x015000=1"

        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_data(5001, 5002, raw)
        pkt.append_pair(20000, "private tag")
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
        self.assertEqual(b"private tag", msg.get(20000))

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
        self.assertEqual(b"private tag", msg.get(20000))
        return

    def test_embedded_equals_96_no_95(self):
        """Test a Logon with 96 but no 95, and an embedded equals."""

        raw = b"8=FIX.4.2" + SOH_STR + \
              b"9=169" + SOH_STR + \
              b"35=A" + SOH_STR + \
              b"52=20171213-01:41:08.063" + SOH_STR + \
              b"49=HelloWorld" + SOH_STR + \
              b"56=1234" + SOH_STR + \
              b"34=1" + SOH_STR + \
              b"96=ABC=DE" + SOH_STR + \
              b"98=0" + SOH_STR + \
              b"108=30" + SOH_STR + \
              b"554=HelloWorld" + SOH_STR + \
              b"8013=Y" + SOH_STR + \
              b"10=166" + SOH_STR

        parser = FixParser()
        parser.append_buffer(raw)
        msg = parser.get_message()

        self.assertIsNotNone(msg)
        return

    def test_simplefix_on_split_execution_report(self):
        """Test parsing with length and data appended separately."""

        part1 = b'8=FIX.4.2\x019=606\x0135=n\x0134=18\x01369=XX\x01' \
                b'52=XXXXXXXX-XX:XX:XX.XXX\x0143=Y\x0149=CME\x0150=G\x01' \
                b'56=XXXXXXX\x0157=NULL\x01122=XXXXXXXX-XX:XX:XX.XXX\x01' \
                b'143=XX\x01212=481\x01213=<RTRF>8=FIX.4'

        part2 = b'.2\x019=XXX\x0135=8\x0134=2087\x01369=2122\x01' \
                b'52=XXXXXXXX-XX:XX:XX.XXX\x0149=CME\x0150=G\x01' \
                b'56=XXXXXXX\x0157=XXXXXXXXXX\x01143=XXXXX\x011=XXXXXXXX\x01' \
                b'6=X\x0111=XXXXX\x0114=XX\x0117=XXXXXXXXXXXXXXXXXXXXXXX\x01' \
                b'20=X\x0131=XXXXXX\x0132=X\x0137=XXXXXXXXXXXX\x0138=XXX\x01' \
                b'39=X\x0140=X\x0141=X\x0144=XXXXXX\x0148=XXXXXX\x0154=X\x01' \
                b'55=XX\x0159=X\x0160=XXXXXXXX-XX:XX:XX.XXX\x01' \
                b'75=XXXXXXXX\x01107=XXXX\x01150=X\x01151=XX\x01167=FUT\x01' \
                b'337=TRADE\x01375=CME000A\x01432=XXXXXXXX\x01' \
                b'442=1\x01527=XXXXXXXXXXXXXXXXXXXXXXXX\x011028=Y\x01' \
                b'1057=Y\x015979=XXXXXXXXXXXXXXXXXXX\x019717=XXXXX\x01' \
                b'37711=XXXXXX\x0110=171\x01</RTRF>\x0110=169\x01'

        # Test append / append / parse
        parser = FixParser()
        parser.append_buffer(part1)
        parser.append_buffer(part2)
        msg = parser.get_message()
        self.assertEqual(msg.get(10), b'169')

        # Test append / parse / append / parse
        parser = FixParser()
        parser.append_buffer(part1)
        msg = parser.get_message()
        self.assertEqual(msg, None)

        parser.append_buffer(part2)
        msg = parser.get_message()
        checksum = msg.get(10)
        self.assertEqual(checksum, b'169')
        return

    def test_stop_tag(self):
        """Test termination using alternative tag number."""

        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_pair(29, "A")
        pkt.append_pair(20000, "xxx")
        pkt.append_pair(10, "000")
        buf = pkt.encode()

        p = FixParser()
        p.set_message_terminator(tag=20000)
        p.append_buffer(buf)
        m = p.get_message()

        self.assertIsNotNone(m)
        self.assertEqual(b"FIX.4.2", m.get(8))
        self.assertEqual(b"D", m.get(35))
        self.assertEqual(b"A", m.get(29))
        self.assertEqual(b"xxx", m.get(20000))
        self.assertEqual(False, 10 in m)
        return

    def test_stop_char_with_field_terminator(self):
        """Test stop character with field terminator."""

        buf = \
            b'8=FIX.4.2\x0135=d\x0134=1\x01369=XX\x01\n' + \
            b'8=FIX.4.2\x0135=d\x0134=2\x01369=XX\x01\n' + \
            b'8=FIX.4.2\x0135=d\x0134=3\x01369=XX\x01\n'

        p = FixParser()
        p.set_message_terminator(char='\n')
        p.append_buffer(buf)

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"1", m.get(34))

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"2", m.get(34))

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"3", m.get(34))
        return

    def test_stop_char_without_field_terminator(self):
        """Test stop character without field terminator."""

        buf = \
            b'8=FIX.4.2\x0135=d\x0134=1\x01369=XX\n' + \
            b'8=FIX.4.2\x0135=d\x0134=2\x01369=XX\n' + \
            b'8=FIX.4.2\x0135=d\x0134=3\x01369=XX\n'

        p = FixParser()
        p.set_message_terminator(char='\n')
        p.append_buffer(buf)

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"1", m.get(34))

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"2", m.get(34))

        m = p.get_message()
        self.assertIsNotNone(m)
        self.assertEqual(b"3", m.get(34))
        return


if __name__ == "__main__":
    unittest.main()
