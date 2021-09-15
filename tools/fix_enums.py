########################################################################
# simplefix
# Copyright (C) 2016-2021, David Arnold.
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

"""FIX Protocol support."""

import lxml.etree
import lxml.objectify
import sys


class FixElement:
    """Base class for all FIX specification elements."""

    def __init__(self):
        """Constructor."""
        self._added = None
        self._updated = None
        self._text_id = None
        return

    @property
    def added(self) -> str:
        """Return 'added' property value."""
        return self._added

    def set_added(self, added: str) -> str:
        """Set 'added' property value."""
        self._added = added
        return added

    @property
    def updated(self) -> str:
        return self._updated

    def set_updated(self, updated: str) -> str:
        self._updated = updated
        return updated

    @property
    def text_id(self) -> str:
        return self._text_id

    def set_text_id(self, text_id: str) -> str:
        self._text_id = text_id
        return text_id

    def set_attribs(self, attrib: dict) -> None:
        """Set properties from a dictionary of parsed attributes."""

        added = attrib.get("added")
        if added:
            self.set_added(added)
        updated = attrib.get("updated")
        if updated:
            self.set_updated(updated)
        text_id = attrib.get("textId")
        if text_id:
            self.set_text_id(text_id)
        return


class DataType(FixElement):
    """FIX basic data type."""

    def __init__(self, name):
        """Constructor."""

        super().__init__()
        self._name = name
        self._added = None
        self._updated = None
        self._text_id = None
        return

    @property
    def name(self):
        return self._name


class Field(FixElement):
    """FIX message field specification."""

    def __init__(self, tag):
        """Constructor."""

        super().__init__()
        self._tag = tag
        self._name = None
        self._type = None
        self._enums = []

        self._values = {}
        return

    @property
    def tag(self):
        return self._tag

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        return

    @property
    def type(self):
        return self._type

    def set_type(self, data_type):
        self._type = data_type
        return

    def append_enum(self, ev):
        self._enums.append(ev)
        self._values[ev.value] = ev
        return ev

    @property
    def enums(self):
        return self._enums

    def get_ev(self, index):
        return self._enums[index]

    def is_enum(self):
        return len(self._enums) > 0

    def get_name_for_value(self, value):
        ev = self._values.get(value)
        if ev:
            return ev.name
        else:
            return "Unknown"


class EnumValue(FixElement):
    """FIX message filed enumerated value."""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._value = None
        self._name = None
        self._sort = None
        return

    @property
    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        return value

    @property
    def name(self):
        return self._name

    def set_name(self, value):
        self._name = value
        return value

    @property
    def sort(self):
        return self._sort

    def set_sort(self, value):
        self._sort = int(value)
        return int(value)

    def set_attribs(self, attrib: dict):
        super().set_attribs(attrib)

        value = attrib.get("value")
        if value:
            self.set_value(value)

        name = attrib.get("symbolicName")
        if name:
            self.set_name(name)

        sort = attrib.get("sort")
        if sort:
            self.set_sort(sort)
        return


class FixDatabase(object):
    """FIX specifications database."""

    def __init__(self):
        """Constructor."""

        self._data_types = {}
        self._fields_by_tag = {}
        return

    def add_datatype(self, name) -> DataType:
        """Add a datatype."""

        d = DataType(name)
        self._data_types[name] = d
        return d

    def count_datatypes(self):
        """Return number of known datatypes."""
        return len(self._data_types)

    def get_data_type(self, name) -> DataType:
        """Get details of a named data type."""
        return self._data_types.get(name)

    @property
    def data_types(self):
        """Get collection of all data types."""
        return self._data_types.values()

    def add_field(self, tag) -> Field:
        """Add a message field."""
        f = Field(tag)
        self._fields_by_tag[tag] = f
        return f

    def count_fields(self):
        """Return number of known fields."""
        return len(self._fields_by_tag)

    @property
    def fields(self):
        """Get collection of all fields."""
        return self._fields_by_tag.values()

    def get_field(self, tag: int) -> Field:
        """Get the field information for a tag."""
        # FIXME: why is the DB key string?  Should be either int or bytes?
        return self._fields_by_tag.get(str(tag))



class Parser:
    """Parser for FIX Repository specification of FIX protocol elements."""

    def __init__(self, database: FixDatabase):
        """Constructor."""
        self._db = database
        return

    def parse(self, raw: bytes):
        """Parse text of XML Repository specification."""

        root: lxml.etree.Element = lxml.objectify.fromstring(raw)

        # Datatypes
        data_types = root.fix.datatypes.getchildren()
        for data_type in data_types:
            attrib = data_type.attrib
            dt = self._db.add_datatype(attrib["name"])
            dt.set_attribs(attrib)

        # Fields
        fields = root.fix.fields.getchildren()
        for field in fields:
            attrib = field.attrib
            tag = attrib.get("id")
            if not tag:
                continue

            f = self._db.add_field(tag)
            name = attrib.get("name")
            if name:
                f.set_name(name)

            f.set_attribs(attrib)

            data_type_name = attrib.get("type")
            if data_type_name:
                data_type = self._db.get_data_type(data_type_name)
                if data_type:
                    f.set_type(data_type)

            children = field.getchildren()
            for child in children:
                ev = EnumValue()
                ev.set_attribs(child.attrib)
                f.append_enum(ev)

        return


########################################################################

if __name__ == "__main__":

    database = FixDatabase()
    parser = Parser(database)

    f = open(sys.argv[1], "rb")
    raw = f.read()
    f.close()

    parser.parse(raw)

    # TagType.
    print("class TagType(int, Enum):")
    print('    """Enumeration of FIX tag types."""')
    print()

    for field in database.fields:
        print(f"    {field.name.upper()} = {field.tag}")

    print("\n")

    # Enums.
    for field in database.fields:
        if not field.is_enum():
            continue

        print(f"class {field.name.upper()}(bytes, Enum):")
        print(f'    """Tag {field.tag} values."""')
        print()
        for enum_value in field.enums:
            print(f"    {enum_value.name} = b'{enum_value.value}'")

        print("\n")

    # Tag type map
    print("""# map of TagType to value enum")
    TAG_VALUE_TYPES = {
        TagType[value.__name__]: value
        for value in globals().values()
        if isinstance(value, EnumMeta) and value not in (Enum, TagType)
    }""")
