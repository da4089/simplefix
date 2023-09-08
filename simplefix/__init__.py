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

"""A simple FIX protocol implementation for Python."""

from .message import FixMessage
from .parser import FixParser
from .constants import *


def pretty_print(buf, sep='|'):
    """Pretty-print a raw FIX buffer.

    :param buf: Byte sequence containing raw message.
    :param sep: Separator character to use for output, default is '|'.
    :returns: Formatted byte array."""

    raw = bytearray(buf)
    cooked = bytearray(len(raw))
    for i, value in enumerate(raw):
        cooked[i] = ord(sep) if value == 1 else value
    return bytes(cooked)


########################################################################
