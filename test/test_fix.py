
import unittest
from simplefix import FixMessage, FixParser


class FixTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_fix_message(self):
        pkt = FixMessage()
        pkt.set_session_version("FIX.4.2")
        pkt.set_message_type('D')
        pkt.append_pair(29, "A")
        buf = pkt.encode()

        p = FixParser()
        p.append_buffer(buf)
        m = p.get_message()

        self.assertIsNotNone(m)
        self.assertEqual(pkt, m)
        return

    def test_raw_empty_message(self):
        pkt = FixMessage()
        pkt.set_raw()
        self.assertEqual("", pkt.encode())
        return

    def test_raw_begin_string(self):
        pkt = FixMessage()
        pkt.set_raw()
        pkt.append_pair(8, "FIX.4.4")
        self.assertEqual("8=FIX.4.4\x01", pkt.encode())
        return

    def test_set_session_version(self):
        pkt = FixMessage()
        pkt.set_session_version("FIX.4.4")
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
        pkt.set_raw()
        pkt.append_pair(9, 42)
        self.assertEqual("9=42\x01", pkt.encode())
        return

    def test_raw_checksum(self):
        pkt = FixMessage()
        pkt.set_raw()
        pkt.append_pair(10, 42)
        self.assertEqual("10=42\x01", pkt.encode())
        return

    def test_raw_msg_type(self):
        pkt = FixMessage()
        pkt.set_raw()
        pkt.append_pair(35, "D")
        self.assertEqual("35=D\x01", pkt.encode())
        return

    def test_empty_message(self):
        pkt = FixMessage()
        self.assertEqual("8=FIX.4.2\x019=5\x0135=0\x0110=161\x01", pkt.encode())
        return



suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(FixTests))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
