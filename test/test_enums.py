import enum
import unittest
from pathlib import Path

from simplefix import constants, enums


def implied_type_enum():
    """Generate an enumeration of tag types based on constants.TAG_* attributes."""
    return enum.unique(enum.Enum('TagType', (
        (name[4:], constant)
        for constant, name in sorted(((int(constant), name)
                                      for name, constant in vars(constants).items()
                                      if name.startswith('TAG_')),
                                     )
        # exclude the tag duplicated to avoid a typo breaking user code
        if name != 'TAG_IOIQlTYIND'
    ), module=__name__, type=int))


def implied_type_enums():
    """Generate enumerations of tag values based on constants.* attributes."""
    return {
        tag: enum.unique(enum.Enum(tag, members, type=bytes, module=__name__))

        for var in vars(constants)
        if var.startswith('TAG_')

        for tag in [var[4:]]

        # create the list of members, then skip if that is empty for this tag type
        for members in [[
            (name[len(tag) + 1:], value)
            for name, value in vars(constants).items()
            if name.startswith(tag + '_')
        ]]
        if members
    }


def render_enums():
    """Render generated enums as code."""
    type_ = implied_type_enum()
    types = implied_type_enums()

    def render_enum(e, id, f=None):
        """Generate Python code for an enum."""
        typeof = type(next(iter(e.__members__.values())).value).__name__
        print(f'class {e.__name__}({typeof}, Enum):', file=f)
        if id:
            print(f'    """Message type {id}"""\n', file=f)
        for value in e.__members__.values():
            print(f'    {value.name} = {value.value!r}', file=f)
        print("\n", file=f)

    with open(Path(__file__).parent.parent / 'simplefix/enums.py', 'w') as f:
        print('from enum import Enum\n\n', file=f)
        render_enum(type_, None, f)
        for name, e in types.items():
            render_enum(e, type_[name].value, f)


class EnumTests(unittest.TestCase):
    """The members of the constants and enums modules are coupled, so this case tests that they are synchronised."""

    def test_enums_from_constants(self):
        """Enums should be derived from the constants."""
        expected_classes = {implied_type_enum(), *implied_type_enums().values()}
        classes = {e for e in vars(enums).values() if type(e) is enum.EnumMeta and e is not enum.Enum}

        # the class names match up
        self.assertSetEqual({c.__name__ for c in classes}, {c.__name__ for c in expected_classes})

        def enum_to_dict(e):
            """Convert an enum to a dictionary which can be used for comparison."""
            # get the key-value pairs in the enum
            result = {v.name: v.value for v in e.__members__.values()}
            # add the name to help debugging
            result['__name__'] = e.__name__
            return result

        # the class members match up
        for expected, actual in zip(sorted(expected_classes, key=lambda e: e.__name__),
                                    sorted(classes, key=lambda e: e.__name__)):
            self.assertEqual(enum_to_dict(expected), enum_to_dict(actual))

    def test_tag_case(self):
        """All constants are uppercase, unless a previous version had them mixed case."""
        self.assertFalse({name
                          for name in dir(constants)
                          if not name.startswith('_') and '_' in name and name.upper() != name
                          } - {'TAG_IOIQlTYIND'})

    def test_examples(self):
        """Enums are generated from constants"""
        tag_id = 25
        tag_type = enums.TagType.IOIQLTYIND

        # TagType has members which map names to numbers
        self.assertEqual(tag_type.value, tag_id)
        # TAG_VALUE_TYPES maps from tag types to the enum they contain (if any)
        self.assertIs(enums.TAG_VALUE_TYPES[tag_type], enums.IOIQLTYIND)
        # generated enums for types contain their possible values
        self.assertEqual(enums.IOIQLTYIND.LOW, constants.IOIQLTYIND_LOW)
        self.assertEqual(enums.IOIQLTYIND.MEDIUM, constants.IOIQLTYIND_MEDIUM)
        self.assertEqual(enums.IOIQLTYIND.HIGH, constants.IOIQLTYIND_HIGH)


if __name__ == "__main__":
    EnumTests.main()
