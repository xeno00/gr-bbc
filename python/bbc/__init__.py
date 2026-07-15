"""GNU Radio BBC anti-jam codec module."""

# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

from .codec import DecodeLimitError, Decoder, Encoder, decode, encode

__all__ = ["DecodeLimitError", "Decoder", "Encoder", "decode", "encode"]

try:
    from .bbc_decoder import BBCDecoder, bbc_decoder
    from .bbc_encoder import BBCEncoder, bbc_encoder
    from .ook_demodulator import OOKDemodulator
    from .ook_modulator import OOKModulator
except ModuleNotFoundError as error:
    # Allow the dependency-free codec to be tested without a GNU Radio
    # installation.  Do not suppress unrelated missing dependencies.
    if error.name != "gnuradio":
        raise
else:
    __all__ += [
        "BBCDecoder",
        "BBCEncoder",
        "OOKDemodulator",
        "OOKModulator",
        "bbc_decoder",
        "bbc_encoder",
    ]
