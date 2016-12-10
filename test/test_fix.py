
import unittest
from simplefix import FixMessage, FixParser


class FixTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_string_with_equals(self):
        msg = FixMessage()
        msg.append_string("8=FIX.4.2")
        self.assertEqual("FIX.4.2", msg.get(8))
        return

    def test_string_without_equals(self):
        msg = FixMessage()
        try:
            msg.append_string("FIX.4.2")
        except ValueError:
            pass

    def test_string_with_bad_tag(self):
        msg = FixMessage()
        try:
            msg.append_string("foo=bar")
        except ValueError:
            pass

    def test_basic_fix_message(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.2")
        pkt.append_pair(35, "D")
        pkt.append_pair(29, "A")
        buf = pkt.encode()

        p = FixParser()
        p.append_buffer(buf)
        m = p.get_message()

        self.assertIsNotNone(m)
        self.assertEqual("FIX.4.2", m.get(8))
        self.assertEqual("D", m.get(35))
        self.assertEqual("A", m.get(29))
        return

    def test_raw_empty_message(self):
        pkt = FixMessage()
        self.assertEqual("", pkt.encode(True))
        return

    def test_raw_begin_string(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual("8=FIX.4.4\x01", pkt.encode(True))
        return

    def test_set_session_version(self):
        pkt = FixMessage()
        pkt.append_pair(8, "FIX.4.4")
        pkt.append_pair(35, "0")
        self.assertEqual("8=FIX.4.4\x019=5\x0135=0\x0110=163\x01", pkt.encode())
        return

    def test_get_repeating(self):
        pkt = FixMessage()
        pkt.append_pair(42, "a")
        pkt.append_pair(42, "b")
        pkt.append_pair(42, "c")

        self.assertEqual("a", pkt.get(42))
        self.assertEqual("b", pkt.get(42, 2))
        self.assertEqual("c", pkt.get(42, 3))
        self.assertEqual("a", pkt.get(42, 1))
        self.assertIsNone(pkt.get(42, 4))
        return

    def test_raw_body_length(self):
        pkt = FixMessage()
        pkt.append_pair(9, 42)
        self.assertEqual("9=42\x01", pkt.encode(True))
        return

    def test_raw_checksum(self):
        pkt = FixMessage()
        pkt.append_pair(10, 42)
        self.assertEqual("10=42\x01", pkt.encode(True))
        return

    def test_raw_msg_type(self):
        pkt = FixMessage()
        pkt.append_pair(35, "D")
        self.assertEqual("35=D\x01", pkt.encode(True))
        return

    def test_empty_message(self):
        try:
            pkt = FixMessage()
        except Exception as e:
            self.assertEqual(type(ValueError), type(e))
        return

    def test_parse_empty_string(self):
        parser = FixParser()
        msg = parser.get_message()
        self.assertIsNone(msg)
        return

    def test_parse_partial_string(self):
        parser = FixParser()
        parser.append_buffer("8=FIX.4.2\x019=")
        msg = parser.get_message()
        self.assertIsNone(msg)

        parser.append_buffer("5\x0135=0\x0110=161\x01")
        msg = parser.get_message()
        self.assertIsNotNone(msg)
        self.assertEqual("FIX.4.2", msg.get(8))
        self.assertEqual("5", msg.get(9))
        self.assertEqual("0", msg.get(35))
        self.assertEqual("161", msg.get(10))
        return

    def test_encode_no_35(self):
        msg = FixMessage()
        msg.append_pair(8, "FIX.4.2")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_encode_no_8(self):
        msg = FixMessage()
        msg.append_pair(35, "D")
        try:
            buf = msg.encode()
        except ValueError:
            pass

    def test_compare_equal(self):
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "0")

        self.assertTrue(a == b)
        return

    def test_compare_not_equal_extra_field(self):
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
        a = FixMessage()
        a.append_pair(8, "FIX.4.2")
        a.append_pair(35, "0")

        b = FixMessage()
        b.append_pair(8, "FIX.4.2")
        b.append_pair(35, "1")

        self.assertFalse(a == b)
        return




suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(FixTests))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
