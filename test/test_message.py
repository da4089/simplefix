#! /usr/bin/env python
########################################################################
# SimpleFIX
# Copyright (C) 2016-2023, David Arnold.
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
import enum
import time
import unittest

from simplefix import FixMessage
from simplefix.message import fix_tag, fix_val


class MessageTests(unittest.TestCase):

    def test_string_with_equals(self):
        """Test field set with tag=value string"""
        msg = FixMessage()
        msg.append_string("8=FIX.4.2")
        self.assertEqual(b"FIX.4.2", msg.get(8))

    def test_string_without_equals(self):
        """Test field set with string not containing equals sign"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_string("FIX.4.2")

    def test_string_with_bad_tag(self):
        """Test field set with bad tag in tag=value string"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_string("foo=bar")

    def test_raw_empty_message(self):
        """Test raw encoding of empty message"""
        pkt = FixMessage()
        self.assertEqual(b"", pkt.encode(True))

    def test_raw_begin_string(self):
        """Test raw encoding of BeginString(8)"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual(b"8=FIX.4.4\x01", pkt.encode(True))

    def test_set_session_version(self):
        """Test minimal message"""
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        pkt.append_pair(35, "0")
        self.assertEqual(b"8=FIX.4.4\x01"
                         b"9=5\x01"
                         b"35=0\x01"
                         b"10=163\x01",
                         pkt.encode())

    def test_get_repeating(self):
        """Test retrieval of repeating field's value"""
        pkt = FixMessage()
        pkt.append_pair(42, "a")
        pkt.append_pair(42, "b")
        pkt.append_pair(42, "c")

        self.assertEqual(b"a", pkt.get(42))
        self.assertEqual(b"b", pkt.get(42, 2))
        self.assertEqual(b"c", pkt.get(42, 3))
        self.assertEqual(b"a", pkt.get(42, 1))
        self.assertIsNone(pkt.get(42, 4))

    def test_raw_body_length(self):
        """Test encoding of BodyLength(9) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(9, 42)
        self.assertEqual(b"9=42\x01", pkt.encode(True))

    def test_raw_checksum(self):
        """Test encoding of CheckSum(10) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(10, 42)
        self.assertEqual(b"10=42\x01", pkt.encode(True))

    def test_cooked_checksum(self):
        """Test calculation of Checksum(10) in cooked mode"""
        msg = FixMessage()
        msg.append_pair(8, b'FIX.4.2')
        msg.append_pair(35, b'D')
        msg.append_pair(5001, b'AAAAA')
        self.assertEqual(b"8=FIX.4.2\x01"
                         b"9=16\x01"
                         b"35=D\x01"
                         b"5001=AAAAA\x01"
                         b"10=048\x01",
                         msg.encode())

    def test_raw_msg_type(self):
        """Test encoding of MessageType(35) in raw mode"""
        pkt = FixMessage()
        pkt.append_pair(35, "D")
        self.assertEqual(b"35=D\x01", pkt.encode(True))

    def test_empty_message(self):
        """Test encoding of empty message"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.encode()

    def test_encode_no_35(self):
        """Test encoding without MessageType(35) field"""
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        with self.assertRaises(ValueError):
            msg.encode()

    def test_encode_no_8(self):
        """Test encoding without BeginString(8) field"""
        msg = FixMessage()
        msg.append_pair(35, "D")
        with self.assertRaises(ValueError):
            msg.encode()

    def test_compare_equal(self):
        """Test comparison of equal messages"""
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")

        self.assertTrue(a == b)

    def test_compare_not_message(self):
        """Test comparison fails against not-FixMessage."""
        msg = FixMessage()
        msg.append_pair(1, 1)
        self.assertFalse(msg == self)

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

    def test_time_defaults(self):
        """Test no supplied timestamp value"""
        msg = FixMessage()
        msg.append_time(52)
        self.assertIsNotNone(msg.get(52))

    def test_time_explicit_none(self):
        """Test explicit None as timestamp value"""
        msg = FixMessage()
        msg.append_time(52, None)
        self.assertIsNotNone(msg.get(52))

    def test_time_float(self):
        """Test floating point timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t)
        self.assertEqual(b"20170116-15:51:12.933", msg.get(52))

    def test_time_datetime(self):
        """Test use of built-in datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_time(52, dt)
        self.assertEqual(b"20170116-15:51:12.933", msg.get(52))

    def test_time_microseconds(self):
        """Test formatting of time values with microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 6)
        self.assertEqual(b"20170116-15:51:12.933458", msg.get(52))

    def test_time_seconds_only(self):
        """Test formatting of time values with no decimal component"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, 0)
        self.assertEqual(b"20170116-15:51:12", msg.get(52))

    def test_time_bad_precision(self):
        """Test bad time precision values"""
        msg = FixMessage()
        t = 1484581872.933458
        with self.assertRaises(ValueError):
            msg.append_time(52, t, 9)

    def test_time_localtime(self):
        """Test non-UTC supplied time values"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_time(52, t, utc=False)

        test = datetime.datetime.fromtimestamp(t)
        s = f"{test:%Y%m%d-%H:%M:%S}.{test.microsecond // 1000}"

        self.assertEqual(s.encode('ascii'), msg.get(52))

    def test_utcts_default(self):
        """Test UTCTimestamp with no supplied timestamp value"""
        msg = FixMessage()
        msg.append_utc_timestamp(52)
        self.assertIsNotNone(msg.get(52))

    def test_utcts_explicit_none(self):
        """Test UTCTimestamp with explicit None timestamp value"""
        msg = FixMessage()
        msg.append_utc_timestamp(52, None)
        self.assertIsNotNone(msg.get(52))

    def test_utcts_float(self):
        """Test UTCTimestamp with floating point value"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t)
        self.assertEqual(b"20170116-15:51:12.933", msg.get(52))

    def test_utcts_datetime(self):
        """Test UTCTimestamp with datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_utc_timestamp(52, dt)
        self.assertEqual(b"20170116-15:51:12.933", msg.get(52))

    def test_utcts_microseconds(self):
        """Test UTCTimestamp formatting of microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t, 6)
        self.assertEqual(b"20170116-15:51:12.933458", msg.get(52))

    def test_utcts_seconds_only(self):
        """Test UTCTimestamp formatting of seconds only"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_timestamp(52, t, 0)
        self.assertEqual(b"20170116-15:51:12", msg.get(52))

    def test_utcts_bad_precision(self):
        """Test UTCTimestamp bad time precision values"""
        msg = FixMessage()
        t = 1484581872.933458
        with self.assertRaises(ValueError):
            msg.append_utc_timestamp(52, t, 9)

    def test_utcto_default(self):
        """Test UTCTimeOnly with no supplied timestamp value"""
        msg = FixMessage()
        msg.append_utc_time_only(273)
        self.assertIsNotNone(msg.get(273))

    def test_utcto_explicit_none(self):
        """Test UTCTimeOnly with explicit None time value"""
        msg = FixMessage()
        msg.append_utc_time_only(273, None)
        self.assertIsNotNone(msg.get(273))

    def test_utcto_float(self):
        """Test UTCTimeOnly with floating point value"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_time_only(273, t)
        self.assertEqual(b"15:51:12.933", msg.get(273))

    def test_utcto_datetime(self):
        """Test UTCTimeOnly with datetime timestamp values"""
        msg = FixMessage()
        t = 1484581872.933458
        dt = datetime.datetime.utcfromtimestamp(t)
        msg.append_utc_time_only(273, dt)
        self.assertEqual(b"15:51:12.933", msg.get(273))

    def test_utcto_microseconds(self):
        """Test UTCTimeOnly formatting of microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_time_only(273, t, 6)
        self.assertEqual(b"15:51:12.933458", msg.get(273))

    def test_utcto_seconds_only(self):
        """Test UTCTimeOnly formatting of seconds only"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_utc_time_only(273, t, 0)
        self.assertEqual(b"15:51:12", msg.get(273))

    def test_utcto_bad_precision(self):
        """Test UTCTimeOnly bad time precision values"""
        msg = FixMessage()
        t = 1484581872.933458
        with self.assertRaises(ValueError):
            msg.append_utc_time_only(273, t, 9)

    def test_utcto_parts_15_51_12(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12)
        self.assertEqual(b"15:51:12", msg.get(1))

    def test_utcto_parts_15_51_12_933(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12, 933)
        self.assertEqual(b"15:51:12.933", msg.get(1))

    def test_utcto_parts_15_51_12_933_458(self):
        msg = FixMessage()
        msg.append_utc_time_only_parts(1, 15, 51, 12, 933, 458)
        self.assertEqual(b"15:51:12.933458", msg.get(1))

    def test_utcto_parts_bad_hour(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 24, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, -1, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, "a", 0, 0)

    def test_utcto_parts_bad_minute(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 60, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, -1, 0)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, "b", 0)

    def test_utcto_parts_bad_seconds(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 61)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, "c")

    def test_utcto_parts_bad_ms(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 1000)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, 0, "d")

    def test_utcto_parts_bad_us(self):
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 0, 1000)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 15, 51, 12, 0, -1)
        with self.assertRaises(ValueError):
            msg.append_utc_time_only_parts(1, 0, 0, 0, 0, "e")

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

    def test_offset_hours(self):
        msg = FixMessage()
        self.assertEqual("Z", msg._tz_offset_string(0))
        self.assertEqual("+01", msg._tz_offset_string(60))
        self.assertEqual("+10", msg._tz_offset_string(600))
        self.assertEqual("-01", msg._tz_offset_string(-60))
        self.assertEqual("-10", msg._tz_offset_string(-600))

    def test_offset_minutes(self):
        msg = FixMessage()
        self.assertEqual("+01:30", msg._tz_offset_string(90))
        self.assertEqual("-01:30", msg._tz_offset_string(-90))
        self.assertEqual("+23:59", msg._tz_offset_string(1439))
        self.assertEqual("-23:59", msg._tz_offset_string(-1439))

    def test_append_tzts_default(self):
        """Test TZTimeOnly with no supplied timestamp value"""
        msg = FixMessage()
        msg.append_tz_time_only(1253)
        self.assertIsNotNone(msg.get(1253))

    def test_append_tzts_none(self):
        """Test TimezoneTimeOnly with explicit None"""
        msg = FixMessage()
        msg.append_tz_timestamp(1253, None)
        self.assertIsNotNone(msg.get(1253))

    @staticmethod
    def calculate_tz_offset(t):
        local = datetime.datetime.fromtimestamp(t)
        utc = datetime.datetime.utcfromtimestamp(t)
        td = local - utc
        offset = int(((td.days * 86400) + td.seconds) / 60)
        return offset

    def test_append_tzts_float(self):
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_timestamp(1132, t)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%03u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec,
             int((t - int(t)) * 1000))
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1132))

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
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1132))

    def test_tzts_microseconds(self):
        """Test formatting of TZTimestamp values with microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_timestamp(1253, t, 6)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u.%06u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec,
             int((t % 1) * 1e6))
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1253))

    def test_tzts_seconds_only(self):
        """Test formatting of TZTimestamp values with seconds only"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_timestamp(1253, t, 0)

        test = time.localtime(t)
        s = "%04u%02u%02u-%02u:%02u:%02u" % \
            (test.tm_year, test.tm_mon, test.tm_mday,
             test.tm_hour, test.tm_min, test.tm_sec)
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1253))

    def test_tzts_bad_precision(self):
        """Test bad TZTimestamp precision value"""
        msg = FixMessage()
        t = 1484581872.933458
        with self.assertRaises(ValueError):
            msg.append_tz_timestamp(1253, t, 9)

    def test_tzto_datetime(self):
        msg = FixMessage()
        t = 1484581872.933458
        local = datetime.datetime.fromtimestamp(t)
        msg.append_tz_time_only(1079, local)

        test = time.localtime(t)
        s = "%02u:%02u:%02u.%03u" % \
            (test.tm_hour, test.tm_min, test.tm_sec, int((t % 1) * 1e3))
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1079))

    def test_tzto_minutes(self):
        """Test TZTimeOnly formatting without seconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_time_only(1079, t, precision=None)

        test = time.localtime(t)
        s = "%02u:%02u" % (test.tm_hour, test.tm_min)
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1079))

    def test_tzto_microseconds(self):
        """Test formatting of TZTimeOnly values with microseconds"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_time_only(1079, t, 6)

        test = time.localtime(t)
        s = "%02u:%02u:%02u.%06u" % \
            (test.tm_hour, test.tm_min, test.tm_sec, int((t % 1) * 1e6))
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1079))

    def test_tzto_seconds_only(self):
        """Test formatting of TZTimeOnly values with seconds only"""
        msg = FixMessage()
        t = 1484581872.933458
        msg.append_tz_time_only(1079, t, 0)

        test = time.localtime(t)
        s = "%02u:%02u:%02u" % \
            (test.tm_hour, test.tm_min, test.tm_sec)
        offset = self.calculate_tz_offset(t)
        if offset == 0:
            s += "Z"
        else:
            offset_hours = abs(offset) / 60
            offset_mins = abs(offset) % 60

            s += "%c%02u" % ("+" if offset > 0 else "-", offset_hours)
            if offset_mins > 0:
                s += ":%02u" % offset_mins

        self.assertEqual(s.encode('ascii'), msg.get(1079))

    def test_tzto_bad_precision(self):
        """Test bad TZTimeOnly precision value"""
        msg = FixMessage()
        t = 1484581872.933458
        with self.assertRaises(ValueError):
            msg.append_tz_time_only(1079, t, 9)

    def test_tzto_parts_15_51_240(self):
        """Test TZTimeOnly with hour and minute components,
         full hour offset"""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, offset=-240)
        self.assertEqual(b"15:51-04", msg.get(1))

    def test_tzto_parts_15_51_270(self):
        """Test TZTimeOnly with hour, minute and second components,
         full hour offset"""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, offset=-270)
        self.assertEqual(b"15:51-04:30", msg.get(1))

    def test_tzto_parts_15_51_12_270(self):
        """Test TZTimeOnly with hour, minute and second components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, offset=-270)
        self.assertEqual(b"15:51:12-04:30", msg.get(1))

    def test_tzto_parts_15_51_12_933_270(self):
        """Test TZTimeOnly with h, m, s and ms components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, offset=-270)
        self.assertEqual(b"15:51:12.933-04:30", msg.get(1))

    def test_tzto_parts_15_51_12_933_458_270(self):
        """Test TZTimeOnly with h, m, s, ms, and us components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, 458, offset=-270)
        self.assertEqual(b"15:51:12.933458-04:30", msg.get(1))

    def test_tzto_parts_15_51_12_933_458_150(self):
        """Test TZTimeOnly with h, m, s, ms, and us components,
         partial hour offset."""
        msg = FixMessage()
        msg.append_tz_time_only_parts(1, 15, 51, 12, 933, 458, offset=150)
        self.assertEqual(b"15:51:12.933458+02:30", msg.get(1))

    def test_tzto_parts_bad_hour(self):
        """Test TZTimeOnly with out-of-range hour components"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 24, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, -1, 0, 0)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, "a", 0, 0)

    def test_tzto_parts_bad_minute(self):
        """Test TZTimeOnly with out-of-range minute components"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 60, 0)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, -1, 0)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 0, "b", 0)

    def test_tzto_parts_bad_seconds(self):
        """Test TZTimeOnly with out-of-range seconds components"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, 61)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, -1)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 0, 0, "c")

    def test_tzto_parts_bad_ms(self):
        """Test TZTimeOnly with out-of-range milliseconds components"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, 12, 1000)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, 12, -1)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 0, 0, 0, "d")

    def test_tzto_parts_bad_us(self):
        """Test TZTimeOnly with out-of-range microseconds components"""
        msg = FixMessage()
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, 12, 0, 1000)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 15, 51, 12, 0, -1)
        with self.assertRaises(ValueError):
            msg.append_tz_time_only_parts(1, 0, 0, 0, 0, "e")

    def test_header_field(self):
        """Test use of header flag"""
        msg = FixMessage()
        msg.append_pair(20000, "third")
        msg.append_pair(20001, "first", header=True)
        msg.append_pair(20002, "second", header=True)
        self.assertEqual(b"20001=first\x01"
                         b"20002=second\x01"
                         b"20000=third\x01",
                         msg.encode(True))

    def test_strings(self):
        """Test adding fields from a sequence of tag=value strings"""
        msg = FixMessage()
        msg.append_strings(["8=FIX.4.4", "35=0"])
        self.assertEqual(b"8=FIX.4.4\x01"
                         b"9=5\x01"
                         b"35=0\x01"
                         b"10=163\x01",
                         msg.encode())

    def test_contains(self):
        """Test use of 'in' and 'not in' operators"""
        msg = FixMessage()
        msg.append_strings(["8=FIX.4.4", "35=0"])
        self.assertIn(8, msg)
        self.assertIn(35, msg)
        self.assertNotIn(9, msg)
        self.assertNotIn(10, msg)

    def test_none_value(self):
        """Test encoding of None value"""
        msg = FixMessage()
        msg.append_pair(99999, None)
        self.assertNotIn(b'99999', msg)

    def test_remove_simple(self):
        """Test removal of single, existent field."""

        msg = FixMessage()
        msg.append_pair(8, b'FIX.4.2')
        self.assertEqual(1, msg.count())
        result = msg.remove(8)
        self.assertEqual(b'FIX.4.2', result)
        self.assertEqual(0, msg.count())

    def test_remove_not_found(self):
        """Test removal of non-existent field."""
        msg = FixMessage()
        msg.append_pair(8, b'FIX.4.2')
        msg.append_pair(35, b'D')
        msg.append_utc_timestamp(52)
        self.assertEqual(3, msg.count())
        result = msg.remove(9)
        self.assertIsNone(result)
        self.assertEqual(3, msg.count())

    def test_remove_nth(self):
        """Test removal of nth field."""
        msg = FixMessage()
        msg.append_pair(99999, 1)
        msg.append_pair(99999, 99999)
        msg.append_pair(99999, 2)
        self.assertEqual(3, msg.count())
        result = msg.remove(99999, 2)
        self.assertEqual(b'99999', result)
        self.assertEqual(2, msg.count())
        self.assertEqual(b'1', msg.get(99999, 1))
        self.assertEqual(b'2', msg.get(99999, 2))

    def test_str(self):
        """Test conversion to string."""
        msg = FixMessage()
        msg.append_pair(1, 1)
        msg.append_pair(2, "foo")
        msg.append_pair(3, b"bar")
        msg.append_pair(4, 3.1415679)

        buffer = str(msg)
        self.assertIsNotNone(buffer)
        self.assertEqual(type(buffer), type("s"))
        self.assertEqual("1=1|2=foo|3=bar|4=3.1415679", buffer)

    def test_to_String(self):
        """Test conversion to string with separator."""
        msg = FixMessage()
        msg.append_pair(1, 1)
        msg.append_pair(2, "foo")
        msg.append_pair(3, b"bar")
        msg.append_pair(4, 3.1415679)

        buffer = msg.to_string('XXX')
        self.assertIsNotNone(buffer)
        self.assertEqual(type(buffer), type("s"))
        self.assertEqual("1=1XXX2=fooXXX3=barXXX4=3.1415679", buffer)

    def test_eq(self):
        """Test __equals__ override."""
        m1 = FixMessage()
        m1.append_pair(1, "one")
        m1.append_pair(2, "two")
        m1.append_pair(2, "to")
        m1.append_pair(2, "too")
        m1.append_pair(3, "end")

        m2 = FixMessage()
        m2.append_pair(3, "end")
        m2.append_pair(2, "too")
        m2.append_pair(2, "to")
        self.assertFalse(m1 == m2)

        m2.append_pair(2, "two")
        m2.append_pair(1, "one")
        self.assertTrue(m1 == m2)

    def test_ne(self):
        """Test __ne__ override."""
        m1 = FixMessage()
        m1.append_pair(1, "one")
        m1.append_pair(2, "two")
        m1.append_pair(2, "to")
        m1.append_pair(2, "too")
        m1.append_pair(3, "end")

        m2 = FixMessage()
        m2.append_pair(3, "end")
        m2.append_pair(2, "too")
        m2.append_pair(2, "to")
        self.assertTrue(m1 != m2)

        m2.append_pair(2, "two")
        m2.append_pair(1, "one")
        self.assertFalse(m1 != m2)

    def test_tag_bytes(self):
        """Test bytes tag value returns bytes."""
        self.assertEqual(b"123", fix_tag(b"123"))
        self.assertEqual(bytes, type(fix_tag(b"123")))

    def test_tag_str(self):
        """Test string tag value returns bytes."""
        self.assertEqual(b"123", fix_tag("123"))
        self.assertEqual(bytes, type(fix_tag("123")))

    def test_tag_int(self):
        """Test integer tag value returns bytes."""
        self.assertEqual(b"123", fix_tag(123))
        self.assertEqual(bytes, type(fix_tag(123)))

    def test_val_bytes(self):
        """Test bytes value returns bytes."""
        self.assertEqual(b"123", fix_val(b"123"))
        self.assertEqual(bytes, type(fix_val(b"123")))

    def test_val_str(self):
        """Test string value returns bytes."""
        self.assertEqual(b"123", fix_val("123"))
        self.assertEqual(bytes, type(fix_val("123")))

    def test_int_value_zero(self):
        """Test integer value: zero."""
        m = FixMessage()
        m.append_pair(34, 0)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=0\x01')

    def test_int_value_one(self):
        """Test integer value: one"""
        m = FixMessage()
        m.append_pair(34, 1)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=1\x01')

    def test_int_value_32bit(self):
        """Test integer value: 2**32-1"""
        m = FixMessage()
        m.append_pair(34, 0xffffffff)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=4294967295\x01')

    def test_int_value_33bit(self):
        """Test integer value: 2**32"""
        m = FixMessage()
        m.append_pair(34, 0xffffffff + 1)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=4294967296\x01')

    def test_int_value_64bit(self):
        """Test integer value: 2**64-1"""
        m = FixMessage()
        m.append_pair(34, 0xffffffffffffffff)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=18446744073709551615\x01')

    def test_int_value_65bit(self):
        """Test integer value: 2**64"""
        m = FixMessage()
        m.append_pair(34, 0xffffffffffffffff + 1)
        b = m.encode(raw=True)
        self.assertEqual(b, b'34=18446744073709551616\x01')

    def test_intenum_value(self):
        class TagEnum(enum.IntEnum):
            BeginString = 8
            Length = 9
            MsgType = 35
            Checksum = 10

        m = FixMessage()
        m.append_pair(TagEnum.MsgType, b'D')
        b = m.encode(raw=True)
        self.assertEqual(b, b'35=D\x01')


if __name__ == "__main__":
    unittest.main()
