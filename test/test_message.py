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
import sys
import time
import unittest

from simplefix import FixMessage


def fix_str(s):
    if sys.version_info.major == 2:
        return bytes(s)
    else:
        return bytes(s, 'ASCII')


class MessageTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_string_with_equals(self):
        """Test field set with tag=value string"""
        msg = FixMessage()
        msg.append_string("8=FIX.4.2")
        self.assertEqual(fix_str("FIX.4.2"), msg.get(8))
        return

    def test_string_without_equals(self):
        """Test field set with string not containing equals sign"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_string("FIX.4.2")
        return

    def test_string_with_bad_tag(self):
        """Test field set with bad tag in tag=value string"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_string("foo=bar")
        return

    def test_raw_empty_message(self):
        """Test raw encoding of empty message"""
        pkt = FixMessage()
        self.assertEqual(fix_str(""), pkt.encode(True))
        return

    def test_raw_begin_string(self):
        """Test raw encoding of BeginString(8)"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual(fix_str("8=FIX.4.4\x01"), pkt.encode(True))
        return

    def test_set_session_version(self):
        """Test minimal message"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        pkt.append_pair(35, "0")
        self.assertEqual(fix_str("8=FIX.4.4\x01"
                                  "9=5\x01"
                                  "35=0\x01"
                                  "10=163\x01"),
                         pkt.encode())
        return

    def test_get_repeating(self):
        """Test retrieval of repeating field's value"""
        pkt = FixMessage()
        pkt.append_pair(42, "a")
        pkt.append_pair(42, "b")
        pkt.append_pair(42, "c")

        self.assertEqual(fix_str("a"), pkt.get(42))
        self.assertEqual(fix_str("b"), pkt.get(42, 2))
        self.assertEqual(fix_str("c"), pkt.get(42, 3))
        self.assertEqual(fix_str("a"), pkt.get(42, 1))
        self.assertIsNone(pkt.get(42, 4))
        return

    def test_raw_body_length(self):
        """Test encoding of BodyLength(9) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(9, 42)
        self.assertEqual(fix_str("9=42\x01"), pkt.encode(True))
        return

    def test_raw_checksum(self):
        """Test encoding of CheckSum(10) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(10, 42)
        self.assertEqual(fix_str("10=42\x01"), pkt.encode(True))
        return

    def test_raw_msg_type(self):
        """Test encoding of MessageType(35) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(35, "D")
        self.assertEqual(fix_str("35=D\x01"), pkt.encode(True))
        return

    def test_empty_message(self):
        """Test encoding of empty message"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.encode()
        return

    def test_encode_no_35(self):
        """Test encoding without MessageType(35) field"""
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        with self.assertRaises(ValueError):
            msg.encode()
        return

    def test_encode_no_8(self):
        """Test encoding without BeginString(8) field"""
        msg = FixMessage()
        msg.append_pair(35, "D")
        with self.assertRaises(ValueError):
            msg.encode()
        return

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

        fields = []
        for tag, _ in msg:
            fields.append(int(tag))

        self.assertEqual([8, 35, 108, 141, 383], fields)
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

        self.assertEqual(fix_str("20170116-15:51:12.933"), msg.get(52))
        return

    def test_time_datetime(self):
        """Test use of built-in datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_time(52, dt)

        self.assertEqual(fix_str("20170116-15:51:12.933"), msg.get(52))
        return

    def test_time_microseconds(self):
        """Test formatting of time values with microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 6)

        self.assertEqual(fix_str("20170116-15:51:12.933458"), msg.get(52))
        return

    def test_time_seconds_only(self):
        """Test formatting of time values with no decimal component"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 0)

        self.assertEqual(fix_str("20170116-15:51:12"), msg.get(52))
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
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec,
             int((t - int(t)) * 1000))
        self.assertEqual(fix_str(s), msg.get(52))
        return

    def test_utcts_default(self):
        """Test UTCTimestamp with no supplied timestamp value"""
        msg = FixMessage()
        msg.append_utc_timestamp(52)
        return

    def test_utcts_explicit_none(self):
        """Test UTCTimestamp with explicit None timestamp value"""
        msg = FixMessage()
        msg.append_utc_timestamp(52, None)
        return

    def test_utcts_float(self):
        """Test UTCTimestamp with floating point value"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t)

        self.assertEqual(fix_str("20170116-15:51:12.933"), msg.get(52))
        return

    def test_utcts_datetime(self):
        """Test UTCTimestamp with datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_utc_timestamp(52, dt)

        self.assertEqual(fix_str("20170116-15:51:12.933"), msg.get(52))
        return

    def test_utcts_microseconds(self):
        """Test UTCTimestamp formatting of microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t, 6)

        self.assertEqual(fix_str("20170116-15:51:12.933458"), msg.get(52))
        return

    def test_utcts_seconds_only(self):
        """Test UTCTimestamp formatting of seconds only"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t, 0)

        self.assertEqual(fix_str("20170116-15:51:12"), msg.get(52))
        return

    def test_utcts_bad_precision(self):
        """Test UTCTimestamp bad time precision values"""
        msg = FixMessage()
        t = 1484581872.933458

        with self.assertRaises(ValueError):
            msg.append_utc_timestamp(52, t, 9)
        return

    # FIXME: utcto tests

    def test_utcto_parts_15_51_12(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12)
        self.assertEqual(fix_str("15:51:12"), msg.get(1))
        return

    def test_utcto_parts_15_51_12_933(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12, 933)
        self.assertEqual(fix_str("15:51:12.933"), msg.get(1))
        return

    def test_utcto_parts_15_51_12_933_458(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12, 933, 458)
        self.assertEqual(fix_str("15:51:12.933458"), msg.get(1))
        return

    def test_utcto_parts_bad_hour(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 24, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, -1, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, "a", 0, 0)
        return

    def test_utcto_parts_bad_minute(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 60, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, -1, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, "b", 0)
        return

    def test_utcto_parts_bad_seconds(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 61)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, "c")
        return

    def test_utcto_parts_bad_ms(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 1000)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, 0, "d")
        return

    def test_utcto_parts_bad_us(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 0, 1000)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 0, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, 0, 0, "e")
        return

    def test_offset_range(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg._tz_offset_string(1500)
        with self.assertRaises(ValueError):
            msg._tz_offset_string(1440)

        msg._tz_offset_string(1439)
        msg._tz_offset_string(0)
        msg._tz_offset_string(-1439)

        with self.assertRaises(ValueError):
            msg._tz_offset_string(-1440)
        with self.assertRaises(ValueError):
            msg._tz_offset_string(-1500)
        return

    def test_offset_hours(self):
        msg = FixMessage()
        self.assertEqual("Z", msg._tz_offset_string(0))
        self.assertEqual("+01", msg._tz_offset_string(60))
        self.assertEqual("+10", msg._tz_offset_string(600))
        self.assertEqual("-01", msg._tz_offset_string(-60))
        self.assertEqual("-10", msg._tz_offset_string(-600))
        return

    def test_offset_minutes(self):
        msg = FixMessage()
        self.assertEqual("+01:30", msg._tz_offset_string(90))
        self.assertEqual("-01:30", msg._tz_offset_string(-90))
        self.assertEqual("+23:59", msg._tz_offset_string(1439))
        self.assertEqual("-23:59", msg._tz_offset_string(-1439))
        return

    def test_append_tzts_float(self):
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_timestamp(1132, t)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec,
             int((t - int(t)) * 1000))
        offset = int((datetime.datetime.fromtimestamp(t) -
                      datetime.datetime.utcfromtimestamp(t)).total_seconds()
                     / 60)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(fix_str(s), msg.get(1132))
        return

    def test_append_tzts_datetime(self):
        msg = FixMessage()
        t = 1484581872.933458
        local = datetime.datetime.fromtimestamp(t)
        msg.append_tz_timestamp(1132, local)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec,
             int((t - int(t)) * 1000))
        offset = int((datetime.datetime.fromtimestamp(t) -
                      datetime.datetime.utcfromtimestamp(t)).total_seconds()
                     / 60)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(fix_str(s), msg.get(1132))
        return

    def test_tzto_minutes(self):
        """Test TZTimeOnly formatting without seconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_time_only(1079, t, precision=None)

        test = time.localtime(t)
        s = "%02u:%02u" % (test.tm_hour, test.tm_min)
        offset = int((datetime.datetime.fromtimestamp(t) -
                      datetime.datetime.utcfromtimestamp(t)).total_seconds()
                     / 60)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(fix_str(s), msg.get(1079))
        return

    def test_tzto_parts_15_51_240(self):
        """Test TZTimeOnly with hour and minute components,
         full hour offset"""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, offset=-240)
        self.assertEqual(fix_str("15:51-04"), msg.get(1))
        return

    def test_tzto_parts_15_51_270(self):
        """Test TZTimeOnly with hour, minute and second components,
         full hour offset"""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, offset=-270)
        self.assertEqual(fix_str("15:51-04:30"), msg.get(1))
        return

    def test_tzto_parts_15_51_12_270(self):
        """Test TZTimeOnly with hour, minute and second components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, offset=-270)
        self.assertEqual(fix_str("15:51:12-04:30"), msg.get(1))
        return

    def test_tzto_parts_15_51_12_933_270(self):
        """Test TZTimeOnly with h, m, s and ms components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, offset=-270)
        self.assertEqual(fix_str("15:51:12.933-04:30"), msg.get(1))
        return

    def test_tzto_parts_15_51_12_933_458_270(self):
        """Test TZTimeOnly with h, m, s, ms, and us components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, 458, offset=-270)
        self.assertEqual(fix_str("15:51:12.933458-04:30"), msg.get(1))
        return

    def test_tzto_parts_15_51_12_933_458_150(self):
        """Test TZTimeOnly with h, m, s, ms, and us components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, 458, offset=150)
        self.assertEqual(fix_str("15:51:12.933458+02:30"), msg.get(1))
        return

    def test_header_field(self):
        """Test use of header flag"""
        msg = FixMessage()
        msg.append_pair(20000, "third")
        msg.append_pair(20001, "first", header=True)
        msg.append_pair(20002, "second", header=True)
        self.assertEqual(fix_str("20001=first\x01"
                                  "20002=second\x01"
                                  "20000=third\x01"),
                         msg.encode(True))
        return

    def test_strings(self):
        """Test adding fields from a sequence of tag=value strings"""
        msg = FixMessage()
        msg.append_strings(["8=FIX.4.4", "35=0"])
        self.assertEqual(fix_str("8=FIX.4.4\x01"
                                  "9=5\x01"
                                  "35=0\x01"
                                  "10=163\x01"),
                         msg.encode())
        return


if __name__ == "__main__":
    unittest.main()
