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

import datetime
import time
import unittest
from simplefix import FixMessage


class MessageTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_string_with_equals(self):
        """Test field set with tag=value string"""
        msg = FixMessage()
        msg.append_string("8=FIX.4.2")
        self.assertEqual("FIX.4.2", msg.get(8))
        return

    def test_string_without_equals(self):
        """Test field set with string not containing equals sign"""
        msg = FixMessage()
        try:
            msg.append_string("FIX.4.2")
        except ValueError:
            pass

    def test_string_with_bad_tag(self):
        """Test field set with bad tag in tag=value string"""
        msg = FixMessage()
        try:
            msg.append_string("foo=bar")
        except ValueError:
            pass

    def test_raw_empty_message(self):
        """Test raw encoding of empty message"""
        pkt = FixMessage()
        self.assertEqual("", pkt.encode(True))
        return

    def test_raw_begin_string(self):
        """Test raw encoding of BeginString(8)"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual("8=FIX.4.4\x01", pkt.encode(True))
        return

    def test_set_session_version(self):
        """Test minimal message"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        pkt.append_pair(35, "0")
        self.assertEqual("8=FIX.4.4\x019=5\x0135=0\x0110=163\x01", pkt.encode())
        return

    def test_get_repeating(self):
        """Test retrieval of repeating field's value"""
        pkt = FixMessage()
        pkt.append_pair(42, "a")
        pkt.append_pair(42, "b")
        pkt.append_pair(42, "c")

        self.assertEqual("a", pkt.get(42))
        self.assertEqual("b", pkt.get(42, 2))
        self.assertEqual("c", pkt.get(42, 3))
        self.assertEqual("a", pkt.get(42, 1))
        self.assertIsNone(pkt.get(42, 4))
        return

    def test_raw_body_length(self):
        """Test encoding of BodyLength(9) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(9, 42)
        self.assertEqual("9=42\x01", pkt.encode(True))
        return

    def test_raw_checksum(self):
        """Test encoding of CheckSum(10) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(10, 42)
        self.assertEqual("10=42\x01", pkt.encode(True))
        return

    def test_raw_msg_type(self):
        """Test encoding of MessageType(35) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(35, "D")
        self.assertEqual("35=D\x01", pkt.encode(True))
        return

    def test_empty_message(self):
        """Test encoding of empty message"""
        try:
            msg = FixMessage()
            buf = msg.encode()
        except Exception as e:
            self.assertEqual(ValueError, type(e))
        return

    def test_encode_no_35(self):
        """Test encoding without MessageType(35) field"""
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_encode_no_8(self):
        """Test encoding without BeginString(8) field"""
        msg = FixMessage()
        msg.append_pair(35, "D")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_compare_equal(self):
        """Test comparison of equal messages"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")

        self.assertTrue(a == b)
        return

    def test_compare_not_equal_extra_field_in_a(self):
        """Test comparison of extra field in this message"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")
        a.append_pair(42000, "something")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")

        self.assertFalse(a == b)
        return

    def test_compare_not_equal_extra_field_in_b(self):
        """Test comparison of other message with extra field"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")
        b.append_pair(42000, "something")

        self.assertFalse(a == b)
        return

    def test_compare_not_equal_different_tags(self):
        """Test comparison of different tagged fields"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")
        a.append_pair(42000, "something")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "1")
        b.append_pair(24000, "something")

        self.assertFalse(a == b)
        return

    def test_compare_not_equal_different_values(self):
        """Test comparison of unequal message field values"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "1")

        self.assertFalse(a == b)
        self.assertFalse(b == a)
        return

    def test_count(self):
        """Test count of message fields"""
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        msg.append_pair(35, "A")
        msg.append_pair(108, 30)
        self.assertEqual(3, msg.count())

        msg.append_pair(141, "N")
        msg.append_pair(383, 16384)
        self.assertEqual(5, msg.count())
        return

    def test_sequence_access(self):
        """Test sequence access to message fields"""
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        msg.append_pair(35, "A")
        msg.append_pair(108, 30)
        msg.append_pair(141, "N")
        msg.append_pair(383, 16384)

        self.assertEqual(35, msg[1][0])
        self.assertEqual(141, msg[3][0])

        l = []
        for tag, _ in msg:
            l.append(int(tag))

        self.assertEqual([8, 35, 108, 141, 383], l)
        return

    def test_time_defaults(self):
        """Test no supplied timestamp value"""
        msg = FixMessage()
        msg.append_time(52)
        return

    def test_time_explicit_none(self):
        """Test explicit None as timestamp value"""
        msg = FixMessage()
        msg.append_time(52, None)
        return

    def test_time_float(self):
        """Test floating point timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t)

        self.assertEqual("20170116-15:51:12.933", msg.get(52))
        return

    def test_time_datetime(self):
        """Test use of built-in datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_time(52, dt)

        self.assertEqual("20170116-15:51:12.933", msg.get(52))
        return

    def test_time_microseconds(self):
        """Test formatting of time values with microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 6)

        self.assertEqual("20170116-15:51:12.933458", msg.get(52))
        return

    def test_time_seconds_only(self):
        """Test formatting of time values with no decimal component"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 0)

        self.assertEqual("20170116-15:51:12", msg.get(52))
        return

    def test_time_bad_precision(self):
        """Test bad time precision values"""
        msg = FixMessage()
        t = 1484581872.933458

        with self.assertRaises(ValueError):
           msg.append_time(52, t, 9)
        return

    def test_time_localtime(self):
        """Test non-UTC supplied time values"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, utc=False)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % (test.tm_year, test.tm_mon, test.tm_mday, test.tm_hour, test.tm_min, test.tm_sec, int((t - int(t)) * 1000))
        self.assertEqual(s, msg.get(52))
        return

    def test_header_field(self):
        """Test use of header flag"""

        msg = FixMessage()
        msg.append_pair(20000, "third")
        msg.append_pair(20001, "first", header=True)
        msg.append_pair(20002, "second", header=True)
        self.assertEqual("20001=first\x0120002=second\x0120000=third\x01",
                         msg.encode(True))
        return

    def test_strings(self):
        """Test adding fields from a sequence of tag=value strings"""

        msg = FixMessage()
        msg.append_strings(["8=FIX.4.4", "35=0"])
        self.assertEqual("8=FIX.4.4\x019=5\x0135=0\x0110=163\x01", msg.encode())
        return


if __name__ == "__main__":
    unittest.main()
