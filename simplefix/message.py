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

# Implements generic FIX protocol.
#
# Each message is a collection of tag+value pairs.  Tags are integers,
# but values are converted to strings when they're set (if not
# before).  The pairs are maintained in order of creation.  Duplicates
# and repeating groups are allowed.
#
# If tags 8, 9 or 10 are not supplied, they will be automatically
# added in the correct location, and with correct values.  You can
# supply these tags in the wrong order for testing error handling.

import datetime
import sys
import time
import warnings

from .constants import SOH_STR


def fix_val(value):
    """Make a FIX value from a string, bytes, or number."""
    if type(value) == bytes:
        return value

    if sys.version_info.major == 2:
        return bytes(value)
    elif type(value) == str:
        return bytes(value, 'UTF-8')
    else:
        return bytes(str(value), 'ASCII')


def fix_tag(value):
    """Make a FIX tag value from string, bytes, or integer."""
    if sys.version_info.major == 2:
        return bytes(value)
    else:
        return bytes(str(value), 'ASCII')


class FixMessage(object):
    """FIX protocol message.

    FIX messages consist of an ordered list of tag=value pairs.  Tags
    are numbers, represented on the wire as strings.  Values may have
    various types, again all presented as strings on the wire.

    This class stores a FIX message: it does not perform any validation
    of the content of tags or values, nor the presence of tags required
    for compliance with a specific FIX protocol version."""

    def __init__(self):
        """Initialise a FIX message."""

        self.begin_string = None
        self.message_type = None
        self.pairs = []
        self.header_index = 0
        return

    def count(self):
        """Return the number of pairs in this message."""
        return len(self.pairs)

    def append_pair(self, tag, value, header=False):
        """Append a tag=value pair to this message.

        :param tag: Integer or string FIX tag number.
        :param value: FIX tag value.
        :param header: Append to header if True; default to body.

        Both parameters are explicitly converted to strings before
        storage, so it's ok to pass integers if that's easier for
        your program logic."""

        if int(tag) == 8:
            self.begin_string = fix_val(value)

        if int(tag) == 35:
            self.message_type = fix_val(value)

        if header:
            self.pairs.insert(self.header_index,
                              (fix_tag(tag),
                               fix_val(value)))
            self.header_index += 1
        else:
            self.pairs.append((fix_tag(tag), fix_val(value)))
        return

    def append_time(self, tag, timestamp=None, precision=3, utc=True,
                    header=False):
        """Append a time field to this message.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time (see below) value to append, or None for now.
        :param precision: Number of decimal digits.  Zero for seconds only,
        three for milliseconds, 6 for microseconds.  Defaults to milliseconds.
        :param utc: Use UTC if True, local time if False.
        :param header: Append to header if True; default to body.

        THIS METHOD IS DEPRECATED!
        USE append_utc_timestamp() OR append_tz_timestamp() INSTEAD.

        Append a timestamp in FIX format from a Python time.time or
        datetime.datetime value.

        Note that prior to FIX 5.0, precision must be zero or three to be
        compliant with the standard."""

        warnings.warn("simplefix.FixMessage.append_time() is deprecated. "
                      "Use append_utc_timestamp() or append_tz_timestamp() "
                      "instead.", DeprecationWarning)
        if not timestamp:
            t = datetime.datetime.utcnow()

        elif type(timestamp) is float:
            if utc:
                t = datetime.datetime.utcfromtimestamp(timestamp)
            else:
                t = datetime.datetime.fromtimestamp(timestamp)

        else:
            t = timestamp

        s = t.strftime("%Y%m%d-%H:%M:%S")
        if precision == 3:
            s += ".%03d" % (t.microsecond / 1000)
        elif precision == 6:
            s += ".%06d" % t.microsecond
        elif precision != 0:
            raise ValueError("Precision should be one of 0, 3 or 6 digits")

        return self.append_pair(tag, s, header=header)

    def append_utc_timestamp(self, tag, timestamp=None, precision=3,
                             header=False):
        """Append a field with a UTCTimestamp value.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time value, see below.
        :param precision: Number of decimal places: 0, 3 (ms) or 6 (us).
        :param header: Append to FIX header if True; default to body.

        The `timestamp` value should be a datetime, such as created by
        datetime.datetime.utcnow(); a float, being the number of seconds
        since midnight 1 Jan 1970 UTC, such as returned by time.time();
        or, None, in which case datetime.datetime.utcnow() is used to
        get the current UTC time.

        Precision values other than zero (seconds), 3 (milliseconds),
        or 6 (microseconds) will raise an exception.  Note that prior
        to FIX 5.0, only values of 0 or 3 comply with the standard."""

        if timestamp is None:
            t = datetime.datetime.utcnow()
        elif type(timestamp) is float:
            t = datetime.datetime.utcfromtimestamp(timestamp)
        else:
            t = timestamp

        s = t.strftime("%Y%m%d-%H:%M:%S")
        if precision == 3:
            s += ".%03d" % (t.microsecond / 1000)
        elif precision == 6:
            s += ".%06d" % t.microsecond
        elif precision != 0:
            raise ValueError("Precision should be one of 0, 3 or 6 digits")

        return self.append_pair(tag, s, header=header)

    def append_utc_time_only(self, tag, timestamp=None, precision=3,
                             header=False):
        """Append a field with a UTCTimeOnly value.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time value, see below.
        :param precision: Number of decimal places: 0, 3 (ms) or 6 (us).
        :param header: Append to FIX header if True; default to body.

        The `timestamp` value should be a datetime, such as created by
        datetime.datetime.utcnow(); a float, being the number of seconds
        since midnight 1 Jan 1970 UTC, such as returned by time.time();
        or, None, in which case datetime.datetime.utcnow() is used to
        get the current UTC time.

        Precision values other than zero (seconds), 3 (milliseconds),
        or 6 (microseconds) will raise an exception.  Note that prior
        to FIX 5.0, only values of 0 or 3 comply with the standard."""

        if timestamp is None:
            t = datetime.datetime.utcnow()
        elif type(timestamp) is float:
            t = datetime.datetime.utcfromtimestamp(timestamp)
        else:
            t = timestamp

        s = t.strftime("%H:%M:%S")
        if precision == 3:
            s += ".%03u" % (t.microsecond / 1000)
        elif precision == 6:
            s += ".%06u" % t.microsecond
        elif precision != 0:
            raise ValueError("Precision should be one of 0, 3 or 6 digits")

        return self.append_pair(tag, s, header=header)

    def append_utc_time_only_parts(self, tag, h, m, s, ms=None, us=None,
                                   header=False):
        """Append a field with a UTCTimeOnly value from components.

        :param tag: Integer or string FIX tag number.
        :param h: Hours, in range 0 to 23.
        :param m: Minutes, in range 0 to 59.
        :param s: Seconds, in range 0 to 59 (60 for leap second).
        :param ms: Optional milliseconds, in range 0 to 999.
        :param us: Optional microseconds, in range 0 to 999.
        :param header: Append to FIX header if True; default to body.

        Formats the UTCTimeOnly value from its components.

        If `ms` or `us` are None, the precision is truncated at
        that point.  Note that seconds are not optional, unlike in
        TZTimeOnly."""

        ih = int(h)
        if ih < 0 or ih > 23:
            raise ValueError("Hour value `h` (%u) out of range "
                             "0 to 23" % ih)
        im = int(m)
        if im < 0 or im > 59:
            raise ValueError("Minute value `m` (%u) out of range "
                             "0 to 59" % im)
        isec = int(s)
        if isec < 0 or isec > 60:
            raise ValueError("Seconds value `s` (%u) out of range "
                             "0 to 60" % isec)
        v = "%02u:%02u:%02u" % (ih, im, isec)

        if ms is not None:
            ims = int(ms)
            if ims < 0 or ims > 999:
                raise ValueError("Milliseconds value `ms` (%u) "
                                 "out of range 0 to 999" % ims)
            v += ".%03u" % ims

            if us is not None:
                ius = int(us)
                if ius < 0 or ius > 999:
                    raise ValueError("Microseconds value `us` (%u) "
                                     "out of range 0 to 999" % ius)
                v += "%03u" % ius

        return self.append_pair(tag, v, header=header)

    def append_tz_timestamp(self, tag, timestamp=None, precision=3,
                            header=False):
        """Append a field with a TZTimestamp value, derived from local time.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time value, see below.
        :param precision: Number of decimal places: 0, 3 (ms) or 6 (us).
        :param header: Append to FIX header if True; default to body.

        The `timestamp` value should be a local datetime, such as created
        by datetime.datetime.now(); a float, being the number of seconds
        since midnight 1 Jan 1970 UTC, such as returned by time.time();
        or, None, in which case datetime.datetime.now() is used to get
        the current local time.

        Precision values other than zero (seconds), 3 (milliseconds),
        or 6 (microseconds) will raise an exception.  Note that prior
        to FIX 5.0, only values of 0 or 3 comply with the standard."""

        # Get float offset from Unix epoch.
        if timestamp is None:
            now = time.time()
        elif type(timestamp) is float:
            now = timestamp
        else:
            now = time.mktime(timestamp.timetuple()) + \
                  (timestamp.microsecond * 1e-6)

        # Get offset of local timezone east of UTC.
        utc = datetime.datetime.utcfromtimestamp(now)
        local = datetime.datetime.fromtimestamp(now)
        offset = int((local - utc).total_seconds() / 60)

        s = local.strftime("%Y%m%d-%H:%M:%S")
        if precision == 3:
            s += ".%03u" % (local.microsecond / 1000)
        elif precision == 6:
            s += ".%06u" % local.microsecond
        elif precision != 0:
            raise ValueError("Precision (%u) should be one of "
                             "0, 3 or 6 digits" % precision)

        s += self._tz_offset_string(offset)
        return self.append_pair(tag, s, header=header)

    def append_tz_time_only(self, tag, timestamp=None, precision=3,
                            header=False):
        """Append a field with a TZTimeOnly value.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time value, see below.
        :param precision: Number of decimal places: 0, 3 (ms) or 6 (us).
        :param header: Append to FIX header if True; default to body.

        The `timestamp` value should be a local datetime, such as created
        by datetime.datetime.now(); a float, being the number of seconds
        since midnight 1 Jan 1970 UTC, such as returned by time.time();
        or, None, in which case datetime.datetime.now() is used to
        get the current UTC time.

        Precision values other than None (minutes), zero (seconds),
        3 (milliseconds), or 6 (microseconds) will raise an exception.
        Note that prior to FIX 5.0, only values of 0 or 3 comply with the
        standard."""

        if timestamp is None:
            t = datetime.datetime.now()
        elif type(timestamp) is float:
            t = datetime.datetime.fromtimestamp(timestamp)
        else:
            t = timestamp

        now = time.mktime(t.timetuple()) + (t.microsecond * 1e-6)
        utc = datetime.datetime.utcfromtimestamp(now)
        offset = int((t - utc).total_seconds() / 60)

        s = t.strftime("%H:%M")
        if precision == 0:
            s += t.strftime(":%S")
        elif precision == 3:
            s += ".%03u" % (t.microsecond / 1000)
        elif precision == 6:
            s += ".%06u" % t.microsecond
        elif precision is not None:
            raise ValueError("Precision should be one of "
                             "None, 0, 3 or 6 digits")

        s += self._tz_offset_string(offset)
        return self.append_pair(tag, s, header=header)

    def append_tz_time_only_parts(self, tag, h, m, s=None, ms=None, us=None,
                                  offset=0, header=False):
        """Append a field with a TZTimeOnly value from components.

        :param tag: Integer or string FIX tag number.
        :param h: Hours, in range 0 to 23.
        :param m: Minutes, in range 0 to 59.
        :param s: Optional seconds, in range 0 to 59 (60 for leap second).
        :param ms: Optional milliseconds, in range 0 to 999.
        :param us: Optional microseconds, in range 0 to 999.
        :param offset: Minutes east of UTC, in range -1439 to +1439.
        :param header: Append to FIX header if True; default to body.

        Formats the TZTimeOnly value from its components.

        If `s`, `ms` or `us` are None, the precision is truncated at
        that point."""

        ih = int(h)
        if ih < 0 or ih > 23:
            raise ValueError("Hour value `h` (%u) out of range "
                             "0 to 23" % ih)

        im = int(m)
        if im < 0 or im > 59:
            raise ValueError("Minute value `m` (%u) out of range "
                             "0 to 59" % im)

        v = "%02u:%02u" % (ih, im)

        if s is not None:
            isec = int(s)
            if isec < 0 or isec > 60:
                raise ValueError("Seconds value `s` (%u) out of range "
                                 "0 to 60" % isec)
            v += ":%02u" % isec

            if ms is not None:
                ims = int(ms)
                if ims < 0 or ims > 999:
                    raise ValueError("Milliseconds value `ms` (%u) "
                                     "out of range 0 to 999" % ims)
                v += ".%03u" % ims

                if us is not None:
                    ius = int(us)
                    if ius < 0 or ius > 999:
                        raise ValueError("Microseconds value `us` (%u) "
                                         "out of range 0 to 999" % ius)
                    v += "%03u" % ius

        v += self._tz_offset_string(offset)
        return self.append_pair(tag, v, header=header)

    def append_string(self, field, header=False):
        """Append a tag=value pair in string format.

        :param field: String "tag=value" to be appended to this message.
        :param header: Append to header if True; default to body.

        The string is split at the first '=' character, and the resulting
        tag and value strings are appended to the message."""

        # Split into tag and value.
        bits = field.split('=', 1)
        if len(bits) != 2:
            raise ValueError("Field missing '=' separator.")

        # Check tag is an integer.
        try:
            tag_int = int(bits[0])
        except ValueError:
            raise ValueError("Tag value must be an integer")

        # Save.
        self.append_pair(tag_int, bits[1], header=header)
        return

    def append_strings(self, string_list, header=False):
        """Append tag=pairs for each supplied string.

        :param string_list: List of "tag=value" strings.
        :param header: Append to header if True; default to body.

        Each string is split, and the resulting tag and value strings
        are appended to the message."""

        for s in string_list:
            self.append_string(s, header=header)
        return

    def append_data(self, len_tag, val_tag, data, header=False):
        """Append raw data, possibly including a embedded SOH.

        :param len_tag: Tag number for length field.
        :param val_tag: Tag number for value field.
        :param data: Raw data byte string.
        :param header: Append to header if True; default to body.

        Appends two pairs: a length pair, followed by a data pair,
        containing the raw data supplied.  Example fields that should
        use this method include: 95/96, 212/213, 354/355, etc."""

        self.append_pair(len_tag, len(data), header=header)
        self.append_pair(val_tag, data, header=header)
        return

    def get(self, tag, nth=1):
        """Return n-th value for tag.

        :param tag: FIX field tag number.
        :param nth: Index of tag if repeating, first is 1.
        :return: None if nothing found, otherwise value matching tag.

        Defaults to returning the first matching value of 'tag', but if
        the 'nth' parameter is overridden, can get repeated fields."""

        tag = fix_tag(tag)
        nth = int(nth)

        for t, v in self.pairs:
            if t == tag:
                nth -= 1
                if nth == 0:
                    return v

        return None

    def encode(self, raw=False):
        """Convert message to on-the-wire FIX format.

        :param raw: If True, encode pairs exactly as provided.

        Unless 'raw' is set, this function will calculate and
        correctly set the BodyLength (9) and Checksum (10) fields, and
        ensure that the BeginString (8), Body Length (9), Message Type
        (35) and Checksum (10) fields are in the right positions.

        This function does no further validation of the message content."""

        buf = b""
        if raw:
            # Walk pairs, creating string.
            for tag, value in self.pairs:
                buf += tag + b'=' + value + SOH_STR

            return buf

        # Cooked.
        for tag, value in self.pairs:
            if int(tag) in (8, 9, 35, 10):
                continue
            buf += tag + b'=' + value + SOH_STR

        # Prepend the message type.
        if self.message_type is None:
            raise ValueError("No message type set")

        buf = b"35=" + self.message_type + SOH_STR + buf

        # Calculate body length.
        #
        # From first byte after body length field, to the delimiter
        # before the checksum (which shouldn't be there yet).
        body_length = len(buf)

        # Prepend begin-string and body-length.
        if not self.begin_string:
            raise ValueError("No begin string set")

        buf = b"8=" + self.begin_string + SOH_STR + \
              b"9=" + fix_val("%u" % body_length) + SOH_STR + \
              buf

        # Calculate and append the checksum.
        checksum = 0
        for c in buf:
            checksum += ord(c) if sys.version_info.major == 2 else c
        buf += b"10=" + fix_val("%03u" % (checksum % 256,)) + SOH_STR

        return buf

    def __eq__(self, other):
        """Compare with another FixMessage.

        :param other: Message to compare.

        Compares the tag=value pairs, message_type and FIX version
        of this message against the `other`."""

        # Check pairs list lengths.
        if len(self.pairs) != len(other.pairs):
            return False

        # Clone our pairs list.
        tmp = []
        for pair in self.pairs:
            tmp.append((pair[0], pair[1]))

        for pair in other.pairs:
            try:
                tmp.remove(pair)
            except ValueError:
                return False

        if len(tmp) > 0:
            return False

        return True

    def __getitem__(self, item_index):
        """Enable messages to be iterated over, and treated as a sequence.

        :param item_index: Numeric index in range 0 to length - 1

        Supports both 'for tag, value in message' usage, and
        'message[n]' access."""

        if item_index >= len(self.pairs):
            raise IndexError

        tag, value = self.pairs[item_index]
        return int(tag), value

    @staticmethod
    def _tz_offset_string(offset):
        """(Internal) Convert TZ offset in minutes east to string."""

        s = ""
        io = int(offset)
        if io == 0:
            s += "Z"
        else:
            if -1440 < io < 1440:
                ho = abs(io) / 60
                mo = abs(io) % 60

                s += "%c%02u" % ("+" if io > 0 else "-", ho)
                if mo != 0:
                    s += ":%02u" % mo

            else:
                raise ValueError("Timezone `offset` (%u) out of range "
                                 "-1439 to +1439 minutes" % io)
        return s


########################################################################
