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


# FIX field delimiter character.
SOH = '\001'


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
        return

    def count(self):
        """Return the number of pairs in this message."""
        return len(self.pairs)

    def append_pair(self, tag, value):
        """Append a tag=value pair to this message.

        :param tag: Integer or string FIX tag number.
        :param value: FIX tag value.

        Both parameters are explicitly converted to strings before
        storage, so it's ok to pass integers if that's easier for
        your program logic."""

        if int(tag) == 8:
            self.begin_string = str(value)

        if int(tag) == 35:
            self.message_type = value

        self.pairs.append((str(tag), str(value)))
        return

    def append_time(self, tag, timestamp=None, precision=3, utc=True):
        """Append a time field to this message.

        :param tag: Integer or string FIX tag number.
        :param timestamp: Time (see below) value to append, or None for now.
        :param precision: Number of decimal digits, defaults to milliseconds.
        :param utc: Use UTC if True, local time if False.

        Append a timestamp in FIX format from a Python time.time or
        datetime.datetime value.

        Note that prior to FIX 5.0, precision must be 3 to be
        compliant with the standard."""

        if not timestamp:
            t = datetime.datetime.utcnow()

        elif type(timestamp) is float:
            if utc:
                t = datetime.datetime.utcfromtimestamp(timestamp)
            else:
                t = datetime.datetime.fromtimestamp(timestamp)

        else:
            t = timestamp

        s = t.strftime("%Y%m%d-%H:%M:%S.")
        if precision == 3:
            s += "%03d" % (t.microsecond / 1000)
        elif precision == 6:
            s += "%06d" % t.microsecond
        else:
            raise ValueError("Precision should be either 3 or 6 digits")

        return self.append_pair(tag, s)

    def append_string(self, field):
        """Append a tag=value pair in string format.

        :param field: String "tag=value" to be appended to this message.

        The string is split at the first '=' character, and the resulting
        tag and value strings are appended to the message."""

        # Split into tag and value.
        l = field.split('=', 1)
        if len(l) != 2:
            raise ValueError("Field missing '=' separator.")

        # Check tag is an integer.
        try:
            tag_int = int(l[0])
        except ValueError:
            raise ValueError("Tag value must be an integer")

        # Save.
        self.append_pair(tag_int, l[1])
        return

    def append_strings(self, string_list):
        """Append tag=pairs for each supplied string.

        :param string_list: List of "tag=value" strings.

        Each string is split, and the resulting tag and value strings
        are appended to the message."""

        for s in string_list:
            self.append_string(s)
        return

    def append_data(self, len_tag, val_tag, data):
        """Append raw data, possibly including a embedded SOH.

        :param len_tag: Tag number for length field.
        :param val_tag: Tag number for value field.
        :param data: Raw data byte string.

        Appends two pairs: a length pair, followed by a data pair,
        containing the raw data supplied.  Example fields that should
        use this method include: 95/96, 212/213, 354/355, etc."""

        self.append_pair(len_tag, len(data))
        self.append_pair(val_tag, data)
        return

    def get(self, tag, nth=1):
        """Return n-th value for tag.

        :param tag: FIX field tag number.
        :param nth: Index of tag if repeating, first is 1.
        :return: None if nothing found, otherwise value matching tag.

        Defaults to returning the first matching value of 'tag', but if
        the 'nth' parameter is overridden, can get repeated fields."""

        str_tag = str(tag)
        nth = int(nth)

        for t, v in self.pairs:
            if t == str_tag:
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

        It does not further validation of the message content."""

        s = ''
        if raw:
            # Walk pairs, creating string.
            for tag, value in self.pairs:
                s += '%s=%s' % (tag, value)
                s += SOH
            return s

        # Cooked.
        for tag, value in self.pairs:
            if int(tag) in (8, 9, 35, 10):
                continue
            s += '%s=%s' % (tag, value)
            s += SOH

        # Prepend the message type.
        if not self.message_type:
            raise ValueError("No message type set")

        s = "35=%s" % self.message_type + SOH + s

        # Calculate body length.
        #
        # From first byte after body length field, to the delimiter
        # before the checksum (which shouldn't be there yet).
        body_length = len(s)

        # Prepend begin-string and body-length.
        if not self.begin_string:
            raise ValueError("No begin string set")

        s = "8=%s" % self.begin_string + SOH + \
            "9=%u" % body_length + SOH + \
            s

        # Calculate and append the checksum.
        checksum = 0
        for c in s:
            checksum += ord(c)
        s += "10=%03u" % (checksum % 256,) + SOH

        return s

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
        return (int(tag), value)



########################################################################
