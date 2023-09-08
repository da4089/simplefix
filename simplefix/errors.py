#! /usr/bin/env python
########################################################################
# SimpleFIX
# Copyright (C) 2018-2023, David Arnold.
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

"""Exceptions."""


class ParserConfigError(Exception):
    """Parser configuration is invalid."""


class ParsingError(Exception):
    """Base class for all parsing errors."""


class TagNotNumberError(ParsingError, ValueError):
    """Tag value could not be converted to integer."""


class RawLengthNotNumberError(ParsingError, ValueError):
    """Raw length value could not be converted to integer."""


class FieldOrderError(ParsingError):
    """Field not found where required by standard."""


class BadChecksumValueError(ParsingError):
    """Checksum (10) value incorrect."""


class BadMessageLengthError(ParsingError):
    """BodyLength (9) value incorrect."""


class IncompleteTagError(ParsingError):
    """And end-of-message byte was read in the middle of a tag."""


class EmptyValueError(ParsingError):
    """A zero-length value was parsed."""
