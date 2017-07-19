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
        msg = FixMessage()
        msg.append_string("8=FIX.4.2")
        self.assertEqual("FIX.4.2", msg.get(8))
        return

    def test_string_without_equals(self):
        msg = FixMessage()
        try:
            msg.append_string("FIX.4.2")
        except ValueError:
            pass

    def test_string_with_bad_tag(self):
        msg = FixMessage()
        try:
            msg.append_string("foo=bar")
        except ValueError:
            pass

    def test_raw_empty_message(self):
        pkt = FixMessage()
        self.assertEqual("", pkt.encode(True))
        return

    def test_raw_begin_string(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual("8=FIX.4.4\x01", pkt.encode(True))
        return

    def test_set_session_version(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        pkt.append_pair(35, "0")
        self.assertEqual("8=FIX.4.4\x019=5\x0135=0\x0110=163\x01", pkt.encode())
        return

    def test_get_repeating(self):
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
        pkt = FixMessage()
        pkt.append_pair(9, 42)
        self.assertEqual("9=42\x01", pkt.encode(True))
        return

    def test_raw_checksum(self):
        pkt = FixMessage()
        pkt.append_pair(10, 42)
        self.assertEqual("10=42\x01", pkt.encode(True))
        return

    def test_raw_msg_type(self):
        pkt = FixMessage()
        pkt.append_pair(35, "D")
        self.assertEqual("35=D\x01", pkt.encode(True))
        return

    def test_empty_message(self):
        try:
            msg = FixMessage()
            buf = msg.encode()
        except Exception as e:
            self.assertEqual(ValueError, type(e))
        return

    def test_encode_no_35(self):
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_encode_no_8(self):
        msg = FixMessage()
        msg.append_pair(35, "D")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_compare_equal(self):
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")

        self.assertTrue(a == b)
        return

    def test_compare_not_equal_extra_field_in_a(self):
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
        msg = FixMessage()
        msg.append_time(52)
        return

    def test_time_explicit_none(self):
        msg = FixMessage()
        msg.append_time(52, None)
        return

    def test_time_float(self):
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t)

        self.assertEqual("20170116-15:51:12.933", msg.get(52))
        return

    def test_time_datetime(self):
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_time(52, dt)

        self.assertEqual("20170116-15:51:12.933", msg.get(52))
        return

    def test_time_microseconds(self):
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 6)

        self.assertEqual("20170116-15:51:12.933458", msg.get(52))
        return

    def test_time_bad_precision(self):
        msg = FixMessage()
        t = 1484581872.933458

        with self.assertRaises(ValueError):
           msg.append_time(52, t, 9)
        return

    def test_time_localtime(self):
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, utc=False)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % (test.tm_year, test.tm_mon, test.tm_mday, test.tm_hour, test.tm_min, test.tm_sec, int((t - int(t)) * 1000))
        self.assertEqual(s, msg.get(52))
        return


if __name__ == "__main__":
    unittest.main()
