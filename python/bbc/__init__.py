#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The presence of this file turns this directory into a Python package

'''
gr-bbc: Baird, Bahn and Collins' concurrent codec for GNU Radio.

BBC encodes a message into a long, sparse codeword by placing one mark per
message bit at a pseudo-random location.  Because the channel model only allows
marks to be *added*, the codeword survives heavy jamming and several messages
can share one codeword.

The codec itself lives in :mod:`bbc.codec` and has no GNU Radio dependency, so
it can be driven from a plain script.
'''

# gr-bbc is pure Python: there is no compiled extension module to import.

from .codec import (Encoder, Decoder, BbcError, DEFAULT_CHECKSUM_BITS,
                    DEFAULT_CHECKSUM_MODE, CHECKSUM_ZEROS, CHECKSUM_SHA256)
from .glowworm import Glowworm, CHECKVALUE
from .bbc_encoder import bbc_encoder
from .bbc_decoder import bbc_decoder
from .OOKDemodulator import OOKDemodulator
from .OOKModulator import OOKModulator

__all__ = [
    'Encoder', 'Decoder', 'BbcError', 'DEFAULT_CHECKSUM_BITS',
    'DEFAULT_CHECKSUM_MODE', 'CHECKSUM_ZEROS', 'CHECKSUM_SHA256',
    'Glowworm', 'CHECKVALUE',
    'bbc_encoder', 'bbc_decoder', 'OOKDemodulator', 'OOKModulator',
]
