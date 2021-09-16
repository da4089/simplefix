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

    @property
    def added(self) -> str:
        """Return FIX version element was added."""
        return self._added

    def set_added(self, added: str) -> str:
        """Set FIX version element was added."""
        self._added = added
        return added

    @property
    def updated(self) -> str:
        """Return FIX version element definition last updated."""
        return self._updated

    def set_updated(self, updated: str) -> str:
        """Set FIX version element definition last updated."""
        self._updated = updated
        return updated

    @property
    def text_id(self) -> str:
        """Return FIX element textual identifier."""
        return self._text_id

    def set_text_id(self, text_id: str) -> str:
        """Set FIX element's textual identifier."""
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


class DataType(FixElement):
    """FIX basic data type."""

    def __init__(self, name):
        """Constructor."""
        super().__init__()
        self._name = name
        self._added = None
        self._updated = None
        self._text_id = None

    @property
    def name(self):
        """Return name of data type."""
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

    @property
    def tag(self):
        """Return field's tag number."""
        return self._tag

    @property
    def name(self):
        """Return field's name."""
        return self._name

    def set_name(self, name: str):
        """Set field's name."""
        self._name = name
        return name

    @property
    def type(self):
        """Return field's type."""
        return self._type

    def set_type(self, data_type):
        """Set field's type."""
        self._type = data_type
        return data_type

    def append_enum(self, ev):
        """Append an allowed value for this enumerated field."""
        self._enums.append(ev)
        self._values[ev.value] = ev
        return ev

    @property
    def enums(self):
        """Return the collection of enumerated values for this field."""
        return self._enums

    def get_ev(self, index):
        """Get the index-th enumerated value for this field."""
        return self._enums[index]

    def is_enum(self):
        """Return True if this field has enumerated values defined."""
        return len(self._enums) > 0

    def get_name_for_value(self, value):
        """Get the name for an enumerated value for this field."""
        ev = self._values.get(value)
        if ev:
            return ev.name
        return "Unknown"


class EnumValue(FixElement):
    """FIX message filed enumerated value."""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self._value = None
        self._name = None
        self._sort = None

    @property
    def value(self):
        """Return the data value for this enumerated value."""
        return self._value

    def set_value(self, value):
        """Set the data value for this enumerated value."""
        self._value = value
        return value

    @property
    def name(self) -> str:
        """Return the name of this enumerated value."""
        return self._name

    def set_name(self, value: str) -> str:
        """Set the name of this enumerated value."""
        self._name = value
        return value

    @property
    def sort(self):
        """Return the sort order of this enumerated value."""
        return self._sort

    def set_sort(self, value):
        """Set the sort order of this enumerated value."""
        self._sort = int(value)
        return int(value)

    def set_attribs(self, attrib: dict):
        """Set all attributes of this enumerated value from dict."""
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


class FixDatabase:
    """FIX specifications database."""

    def __init__(self):
        """Constructor."""
        self._data_types = {}
        self._fields_by_tag = {}

    def add_datatype(self, name: str) -> DataType:
        """Add a datatype."""
        d = DataType(name)
        self._data_types[name] = d
        return d

    def count_datatypes(self):
        """Return number of known datatypes."""
        return len(self._data_types)

    def get_data_type(self, name: str) -> DataType:
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

    def parse(self, text: bytes):
        """Parse text of XML Repository specification."""
        root: lxml.etree.Element = lxml.objectify.fromstring(text)

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


########################################################################

if __name__ == "__main__":

    fix_database = FixDatabase()
    parser = Parser(fix_database)

    with open(sys.argv[1], "rb") as xml_file:
        xml_text = xml_file.read()
        parser.parse(xml_text)

    if fix_database.count_fields() == 0:
        print("Error: no fields parsed from file", file=sys.stderr)
        sys.exit(1)

    # TagType.
    print("class TagType(int, Enum):")
    print('    """Enumeration of FIX tag types."""')
    print()

    for fix_field in fix_database.fields:
        print(f"    {fix_field.name.upper()} = {fix_field.tag}")

    print("\n")

    # Enums.
    for fix_field in fix_database.fields:
        if not fix_field.is_enum():
            continue

        print(f"class {fix_field.name.upper()}(bytes, Enum):")
        print(f'    """Tag {fix_field.tag} values."""')
        print()
        for enum_value in fix_field.enums:
            print(f"    {enum_value.name.upper()} = b'{enum_value.value}'")

        print("\n")

    # Tag type map
    print("""# map of TagType to value enum")
    TAG_VALUE_TYPES = {
        TagType[value.__name__]: value
        for value in globals().values()
        if isinstance(value, EnumMeta) and value not in (Enum, TagType)
    }""")
