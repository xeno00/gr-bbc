"""GNU Radio vector-stream wrapper for the BBC encoder."""

# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import numpy as np
from gnuradio import gr

from .codec import Encoder


class bbc_encoder(gr.sync_block):
    """Encode each fixed-length byte vector into a BBC codeword vector."""

    def __init__(self, message_length: int = 2**7, codeword_length: int = 2**17):
        self._encoder = Encoder(message_length, codeword_length)
        gr.sync_block.__init__(
            self,
            name="BBC Encoder",
            in_sig=[(np.uint8, self._encoder.message_length)],
            out_sig=[(np.uint8, self._encoder.codeword_length)],
        )

    def work(self, input_items, output_items):
        count = min(len(input_items[0]), len(output_items[0]))
        for index in range(count):
            encoded = self._encoder.encode(input_items[0][index])
            output_items[0][index][:] = np.frombuffer(encoded, dtype=np.uint8)
        return count


BBCEncoder = bbc_encoder
