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
            in_sig=[self._item_type(self._encoder.message_length)],
            out_sig=[self._item_type(self._encoder.codeword_length)],
        )

    @staticmethod
    def _item_type(length):
        return np.uint8 if length == 1 else (np.uint8, length)

    def work(self, input_items, output_items):
        count = min(len(input_items[0]), len(output_items[0]))
        for index in range(count):
            encoded = self._encoder.encode(input_items[0][index])
            encoded_array = np.frombuffer(encoded, dtype=np.uint8)
            if self._encoder.codeword_length == 1:
                output_items[0][index] = encoded_array[0]
            else:
                output_items[0][index][:] = encoded_array
        return count


BBCEncoder = bbc_encoder
