#! /usr/bin/env python

import unittest
from test_fix import FixTests


suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(FixTests))


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
