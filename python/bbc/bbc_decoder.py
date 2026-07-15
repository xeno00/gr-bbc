"""GNU Radio general-block wrapper for the BBC decoder."""

# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections import deque
import logging

import numpy as np
from gnuradio import gr

from .codec import DecodeLimitError, Decoder

_LOGGER = logging.getLogger(__name__)


class bbc_decoder(gr.basic_block):
    """Decode codeword vectors and emit zero or more candidate messages."""

    def __init__(
        self,
        message_length: int = 2**7,
        codeword_length: int = 2**17,
        max_candidates: int = 64,
        max_search_nodes: int = 1_000_000,
    ):
        self._decoder = Decoder(
            message_length,
            codeword_length,
            max_candidates=max_candidates,
            max_search_nodes=max_search_nodes,
        )
        self._pending = deque()
        gr.basic_block.__init__(
            self,
            name="BBC Decoder",
            in_sig=[self._item_type(self._decoder.codeword_length)],
            out_sig=[self._item_type(self._decoder.message_length)],
        )

    @staticmethod
    def _item_type(length):
        return np.uint8 if length == 1 else (np.uint8, length)

    def forecast(self, noutput_items, ninputs):
        requirement = 0 if self._pending else 1
        return [requirement] * ninputs

    def general_work(self, input_items, output_items):
        output = output_items[0]
        produced = 0
        consumed = 0

        while produced < len(output):
            while self._pending and produced < len(output):
                message = np.frombuffer(
                    self._pending.popleft(), dtype=np.uint8
                )
                if self._decoder.message_length == 1:
                    output[produced] = message[0]
                else:
                    output[produced][:] = message
                produced += 1

            if produced >= len(output) or consumed >= len(input_items[0]):
                break

            try:
                self._pending.extend(self._decoder.decode(input_items[0][consumed]))
            except DecodeLimitError as error:
                _LOGGER.warning("dropping BBC codeword: %s", error)
            consumed += 1

        if consumed:
            self.consume(0, consumed)
        return produced


BBCDecoder = bbc_decoder
