# simplefix
A simple FIX protocol implementation for Python

[![Build Status](https://travis-ci.org/da4089/simplefix.svg?branch=master)](https://travis-ci.org/da4089/simplefix)
[![Code Health](https://landscape.io/github/da4089/simplefix/master/landscape.svg?style=flat)](https://landscape.io/github/da4089/simplefix/master)
[![Coverage Status](https://coveralls.io/repos/github/da4089/simplefix/badge.svg?branch=master)](https://coveralls.io/github/da4089/simplefix?branch=master)
[![PyPI](https://img.shields.io/pypi/v/simplefix.svg)](https://pypi.python.org/pypi/simplefix)
[![Python](https://img.shields.io/pypi/pyversions/simplefix.svg)](https://pypi.python.org/pypi/simplefix)

FIX (Financial Information eXchange) Protocol is a widely-used,
text-based protocol for interaction between parties in financial
trading.  Banks, brokers, clearing firms, exchanges, and other general
market participants use FIX protocol for all phases of electronic
trading.

Typically, a FIX implementation exists as a FIX Engine: a standalone
service that acts as a gateway for other applications (matching
engines, trading algos, etc) and implements the FIX protocol.  The
most popular Open Source FIX engine is probably one of the versions of
QuickFIX.

This package provides a simple implementation of the FIX
application-layer protocol.  It does no socket handling, and does not
implement FIX recovery or any message persistence.

http://www.fixtradingcommunity.org/pg/structure/tech-specs/fix-protocol
