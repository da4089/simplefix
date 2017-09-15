# -*- python -*-
########################################################################
# SimpleFIX
# Copyright (C) 2017, David Arnold.
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

# Raw data fields, as defined in FIX.5.0sp2 ep228.
RAW_DATA = (
    (90, 91),        # SecureData
    (93, 89),        # Signature
    (95, 96),        # RawData
    (212, 213),      # XmlData
    (348, 349),      # EncodedIssuer
    (350, 351),      # EncodedSecurityDesc
    (352, 353),      # EncodedListExecInst
    (354, 355),      # EncodedText
    (356, 357),      # EncodedSubject
    (358, 359),      # EncodedHeadline
    (360, 361),      # EncodedAllocText
    (362, 363),      # EncodedUnderlyingIssuer
    (364, 365),      # EncodedUnderlyingSecurityDesc
    (445, 446),      # EncodedListStatusText
    (618, 619),      # EncodedLegIssuer
    (621, 622),      # EncodedLegSecurityDesc
    (1277, 1278),    # DerivativeEncodedIssuer
    (1280, 1281),    # DerivativeEncodedSecurityDesc
    (1282, 1283),    # DerivativeSecurityXML
    (1397, 1398),    # EncodedMktSegmDesc
    (1401, 1402),    # EncryptedPassword
    (1403, 1404),    # EncryptedNewPassword
    (1468, 1469),    # EncodedSecurityListDesc
    (1525, 1527),    # EncodedDocumentationText
    (1578, 1579),    # EncodedEventText
    (1620, 1621),    # InstrumentScopeEncodedSecurityDesc
    (1664, 1665),    # EncodedRejectText
    (1678, 1697),    # EncodedOptionExpirationDesc
    (1733, 1734),    # EncodedFirmAllocText
    (2072, 2073),    # EncodedUnderlyingEventText
    (2074, 2075),    # EncodedLegEventText
    (2179, 2180),    # EncodedLegOptionExpirationDesc
    (2111, 2112),    # EncodedAttachment
    (2287, 2288),    # EncodedUnderlyingOptionExpirationDate
    (2351, 2352),    # EncodedComplianceText
    (2372, 2371),    # EncodedTradeContinuationText
    (2481, 2482),    # EncodedMDStatisticDesc
    (2494, 2493),    # EncodedLegDocumentationText
    (2522, 2521),    # EncodedWarningText
    (2637, 2638),    # EncodedMiscFeeSubTypeDesc
    (2651, 2652),    # EncodedCommissionDesc
    (2665, 2666),    # EncodedAllocCommissionDesc
    (40004, 40005),  # EncodedAdditionalTermBondDesc
    (40008, 40009),  # EncodedAdditionalTermBondIssuer
    (40978, 40979),  # EncodedLegStreamText
    (40980, 40981),  # EncodedLegProvisionText
    (40982, 40983),  # EncodedStreamText
    (40984, 40985),  # EncodedPaymentText
    (40986, 40987),  # EncodedProvisionText
    (40988, 40989),  # EncodedUnderlyingStreamText
    (41083, 41084),  # EncodedDeliveryStreamCycleDesc
    (41101, 41101),  # EncodedMarketDisruptionFallbackUnderlierSecurityDesc
    (41107, 41108),  # EncodedExerciseDesc
    (41256, 41257),  # EncodedStreamCommodityDesc
    (41320, 41321),  # EncodedLegAdditionalTermBondDesc
    (41324, 41325),  # EncodedLegAdditionalTermBondIssuer
    (41458, 41459),  # EncodedLegDeliveryStreamCycleDesc
    (41476, 41477),  # EncodedLegMarketDisruptionFallbackUnderlierSecurityDesc
    (41482, 41483),  # EncodedLegExerciseDesc
    (41653, 41654),  # EncodedLegStreamCommodityDesc
    (41710, 41711),  # EncodedUnderlyingAdditionalTermBondDesc
    (41806, 41807),  # EncodedUnderlyingDeliveryStreamCycleDesc
    (41811, 41812),  # EncodedUnderlyingExerciseDesc
    (41873, 41874),  # EncodedUnderlyingMarketDisruptionFallbackUnderlierSecurityDesc
    (41969, 41970),  # EncodedUnderlyingStreamCommodityDesc
    (42025, 42026),  # EncodedUnderlyingAdditionalTermBondIssuer
    (42171, 42172))  # EncodedUnderlyingProvisionText

# Collection of tag numbers representing raw data fields.
RAW_DATA_TAGS = [x[1] for x in RAW_DATA]

# Collection of tag numbers representing raw data length fields.
RAW_LEN_TAGS = [x[0] for x in RAW_DATA]


########################################################################
