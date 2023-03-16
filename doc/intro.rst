.. _intro:

Introduction
============


`FIX <http://www.fixtradingcommunity.org/pg/structure/tech-specs/fix-protocol>`_
(Financial Information eXchange) Protocol is a widely-used,
text-based protocol for interaction between parties in financial
trading.  Banks, brokers, clearing firms, exchanges, and other general
market participants use FIX protocol for all phases of electronic
trading.

Typically, a FIX implementation exists as a FIX Engine: a standalone
service that acts as a gateway for other applications (matching
engines, trading algos, etc) and implements the FIX protocol.  The
most popular Open Source FIX engine is probably one of the versions of
`QuickFIX <https://github.com/quickfix/quickfix>`_.

This package provides a *simple* implementation of the FIX
application-layer protocol.  It does no socket handling, and does not
implement FIX recovery or any message persistence.  It supports the
creation, encoding, and decoding of FIX messages.

