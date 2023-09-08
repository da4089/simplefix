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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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

from .constants import EQUALS_BYTE, SOH_BYTE
from .message import FixMessage, fix_val
from .data import RAW_DATA_TAGS, RAW_LEN_TAGS

from simplefix import errors

from typing import Optional
import warnings


# By default, messages are terminated by the Checksum (10) tag.
DEFAULT_STOP_TAG = 10


class FixParser:
    """FIX protocol message parser.

    This class translates FIX application messages in raw (wire)
    format into instance of the FixMessage class.

    It does not perform any validation of the fields, their presence
    or absence in a particular message, the data types of fields, or
    the values of enumerations.

    It is suitable for streaming processing, accumulating byte data
    from a network connection, and returning complete messages as they
    are delivered, potentially in multiple fragments.
    """

    def __init__(self,
                 allow_empty_values: bool = False,
                 allow_missing_begin_string: bool = False,
                 strip_fields_before_begin_string: bool = True,
                 stop_tag: int = DEFAULT_STOP_TAG,
                 stop_byte: Optional[bytes] = None):
        """Constructor.

        :param allow_empty_values: If set, an empty field value is
        allowed, in violation of the FIX specification which prohibits
        this.
        :param allow_missing_begin_string: If set, an initial field
        other than BeginString (8) is permitted.
        :param strip_fields_before_begin_string: If set, tag:value pairs
        parsed before the BeginString (8) field are ignored.
        :param stop_tag: Tag number for final field in a message.  This
        setting is overridden by stop_byte.
        :param stop_byte: Byte that indicates end of message.  Typically
        CR or LF.  Setting this value overrides stop_tag.
        """
        # Copy raw field length tags.
        self.raw_len_tags = RAW_LEN_TAGS[:]

        # Copy raw field data tags.
        self.raw_data_tags = RAW_DATA_TAGS[:]

        # Internal buffer used to accumulate message data.
        self.buf = b""

        # Parsed "tag=value" pairs, removed from the buffer, but not
        # yet returned as a message.
        self.pairs = []

        # Parsed length of data field.
        self.raw_len = 0

        # Behaviour flags.

        # Stop tag (default).
        self.stop_tag = stop_tag

        # Stop character (optional).
        self.stop_byte = ord(stop_byte) if stop_byte is not None else None

        # Don't insist on an 8= tag at the start of a message.
        self.allow_missing_begin_string = allow_missing_begin_string

        # Don't insist that fields have a non zero-length value.
        self.allow_empty_values = allow_empty_values

        # Discard any parsed fields prior to BeginString (8).
        self.strip_fields_before_begin_string = strip_fields_before_begin_string

        # Validate settings.
        if self.allow_missing_begin_string and \
                self.strip_fields_before_begin_string:
            raise errors.ParserConfigError(
                "Can't set 'allow_missing_begin_string' "
                "and 'strip_fields_before_begin_string' "
                "simultaneously.")

    def set_stop_tag(self, value: int = DEFAULT_STOP_TAG):
        """Set the tag number of the final field in a message.

        :param value: Final field tag number.

        The default value here is CheckSum (10): the parser recognizes
        a 10=xxx field as the end of a message.  Note that this value
        is overridden if a stop_byte is set.
        """
        self.stop_tag = value

    def set_stop_byte(self, value: Optional[bytes] = None):
        """Set a byte value that will terminate a message.

        :param value: Byte (character) value, usually CR or LF.

        If the parser encounters this byte, anywhere in a message, it is
        interpreted as the end of that message.  This is often used when
        multiple messages are recorded in a file, separated by eg. LF.
        Note that this will override the stop_tag value.

        Setting the stop_byte to None will disable it.
        """
        self.stop_byte = ord(value) if value is not None else None

    def set_allow_missing_begin_string(self, value=True):
        """If set, the first field of a message must be BeginString (8).

        :param value: If True, check first field is begin.

        In some cases, especially FIX-encoded stored data, there might
        not be a Begin String (8) at the start of each message.

        Note this value cannot be True if strip_fields_before_begin_string
        is also True.
        """
        self.allow_missing_begin_string = value

    def set_allow_empty_values(self, value=True):
        """Accept a zero-length value when parsing.

        :param value: If False, raise exception for zero-length values

        The FIX specification prohibits zero-length values, instead
        suggesting that the field be omitted from the message entirely.
        Some implementations do allow a zero-length value, and so this
        is accepted by default.

        If this setting is disabled, a ValueHasZeroLengthError is
        raised from get_message() if such a value is encountered.
        """
        self.allow_empty_values = value

    def set_strip_fields_before_begin_string(self, value: bool = True):
        """Choose whether to discard any fields parsed before 8=FIX.

        :param value: If set, discard any fields before the BeginString (8).

        Note that this setting cannot be set if a missing BeginString is
        also permitted.
        """
        self.strip_fields_before_begin_string = value

    def set_message_terminator(self, tag=None, char=None):
        """Set the end-of-message detection scheme.

        :param tag: FIX tag number of terminating field.  Default is 10.
        :param char: Alternative, terminating character.

        THIS METHOD IS DEPRECATED.
        Use set_stop_tag(), set_stop_byte(), or constructor keywords
        instead.

        By default, messages are terminated by the FIX Checksum (10)
        field.  This can be changed to use a different tag, or a reserved
        character using this function.

        Note that only one of 'tag' or 'char' should be set, using a
        named parameter.
        """
        warnings.warn("simplefix.FixParser.set_message_terminator() is "
                      "deprecated. Use set_stop_tag(), set_stop_byte(), "
                      "or constructor keywords instead", DeprecationWarning)

        if tag is not None and char is not None:
            raise ValueError("Only supply one of 'tag' or 'char'.")

        if tag is not None:
            self.stop_tag = tag
            self.stop_byte = None
        else:
            self.stop_tag = None
            self.stop_byte = ord(char) if char is not None else None

    def add_raw(self, length_tag, value_tag):
        """Define the tags used for a private raw data field.

        :param length_tag: tag number of length field.
        :param value_tag: tag number of value field.

        Data fields are not terminated by the SOH character as is usual for
        FIX, but instead have a second, preceding field that specifies the
        length of the value in bytes.  The parser is initialised with all the
        data fields defined in FIX.5.0, but if your application uses private
        data fields, you can add them here, and the parser will process them
        correctly.
        """
        self.raw_len_tags.append(length_tag)
        self.raw_data_tags.append(value_tag)

    def remove_raw(self, length_tag, value_tag):
        """Remove the tags for a data type field.

        :param length_tag: tag number of the length field.
        :param value_tag: tag number of the value field.

        You can remove either private or standard data field definitions in
        case a particular application uses them for a field of a different
        type.
        """
        self.raw_len_tags.remove(length_tag)
        self.raw_data_tags.remove(value_tag)

    def reset(self):
        """Reset the internal parser state.

        This will discard any appended buffer content, and any fields
        parsed so far.
        """
        self.buf = b""
        self.pairs = []
        self.raw_len = 0

    def append_buffer(self, buf):
        """Append a byte string to the parser buffer.

        :param buf: byte string to append.

        The parser maintains an internal buffer of bytes to be parsed.
        As raw data is read, it can be appended to this buffer.  Each
        call to get_message() will try to remove the bytes of a
        complete messages from the head of the buffer.
        """
        self.buf += fix_val(buf)

    def get_buffer(self):
        """Return a reference to the internal buffer."""
        return self.buf

    def get_message(self):
        """Process the accumulated buffer and return the first message.

        If the buffer starts with FIX fields other than BeginString
        (8), these are discarded until the start of a message is
        found.

        If no BeginString (8) field is found, this function returns
        None.  Similarly, if (after a BeginString) no Checksum (10)
        field is found, the function returns None.

        Otherwise, it returns a simplefix.FixMessage instance
        initialised with the fields from the first complete message
        found in the buffer.
        """
        # Break buffer into tag=value pairs.
        start: int = 0
        point: int = 0
        tag: int = 0
        in_tag: bool = True
        eom: bool = False

        while point < len(self.buf):
            b = self.buf[point]

            if in_tag:
                # Check for end of tag.
                if b == EQUALS_BYTE:   # skipcq: PYL-R1724
                    tag_string = self.buf[start:point]
                    point += 1

                    try:
                        tag = int(tag_string)
                    except ValueError as e:
                        raise errors.TagNotNumberError(*e.args)

                    if tag in self.raw_data_tags and self.raw_len > 0:
                        # Try to extract the data value.
                        if self.raw_len > len(self.buf) - point:
                            # The buffer doesn't yet contain all the raw data,
                            # so wait for more to be added.
                            break

                        # We've got enough buffer to extract the raw data value.
                        value = self.buf[point:point + self.raw_len]
                        self.buf = self.buf[point + self.raw_len + 1:]
                        self.raw_len = 0
                        point = 0

                        self.pairs.append((tag, value))

                        # Expect a tag (or EOM) next.
                        in_tag = True

                    else:
                        # After EQUALS_BYTE, expect a value.
                        in_tag = False

                    start = point
                    continue

                elif b == self.stop_byte:
                    if point != 0:
                        # Stop byte in the middle of a tag.
                        raise errors.IncompleteTagError(self.buf[:point])

                    # stop_byte follows field terminator byte.
                    eom = True
                    self.buf = self.buf[1:]
                    break

            else:  # not in_tag
                if b in (SOH_BYTE, self.stop_byte):
                    value = self.buf[start:point]
                    if not self.allow_empty_values and len(value) == 0:
                        raise errors.EmptyValueError(tag)

                    self.pairs.append((tag, value))
                    self.buf = self.buf[point + 1:]

                    # Check for a stop_byte without a preceding end-of-field.
                    if b == self.stop_byte:
                        eom = True
                        break

                    # Check for end of message tag.
                    if tag == self.stop_tag:
                        break

                    # If this was a raw data length tag, save the length value.
                    if tag in self.raw_len_tags:
                        try:
                            self.raw_len = int(value)
                        except ValueError as e:
                            raise errors.RawLengthNotNumberError(*e.args)

                    # Reset to look for next tag.
                    point = 0
                    start = point
                    in_tag = True

                    # Loop (point already advanced when truncating the buffer).
                    continue

            # Advance to next byte in the string and loop.
            point += 1

        # At this point, we have a sequence of pairs parsed from the buffer,
        # and have either a) run of of buffer, b) hit the end-of-message
        # character, or c) seen the end-of-message tag (and value).

        # No pairs, so no message, so just return None.
        if len(self.pairs) == 0:
            return None

        # Strip leading junk pairs.
        if self.strip_fields_before_begin_string:
            while self.pairs and self.pairs[0][0] != 8:
                # Discard pairs until we find the beginning of a message.
                self.pairs.pop(0)

            if len(self.pairs) == 0:
                return None

        # Check first pair is FIX BeginString.
        if not self.allow_missing_begin_string and self.pairs[0][0] != 8:
            raise errors.FieldOrderError()

        # If we don't have an explicit end-of-message byte, check
        # the last pair has the configured stop_tag, otherwise
        # return None and wait for more data.
        if not eom and self.pairs[-1][0] != self.stop_tag:
            return None

        # Extract message.
        m = FixMessage()
        for tag, value in self.pairs:
            m.append_pair(tag, value)
        self.pairs = []

        return m


########################################################################
