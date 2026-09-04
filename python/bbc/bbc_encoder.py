#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr

from .codec import Encoder, DEFAULT_CHECKSUM_BITS, DEFAULT_CHECKSUM_MODE


class bbc_encoder(gr.sync_block):
    """BBC encoder: one message vector in, one codeword vector out.

    Input and output are vectors of unsigned bytes, ``message_length`` and
    ``codeword_length`` long respectively.
    """

    def __init__(self, message_length=2**7, codeword_length=2**17,
                 checksum_length=DEFAULT_CHECKSUM_BITS,
                 checksum_mode=DEFAULT_CHECKSUM_MODE):
        message_length = int(message_length)
        codeword_length = int(codeword_length)

        gr.sync_block.__init__(
            self,
            name="BBC Encoder",
            in_sig=[(np.uint8, message_length)],
            out_sig=[(np.uint8, codeword_length)])

        self.encoder = Encoder(message_length, codeword_length,
                               int(checksum_length), checksum_mode)

    def work(self, input_items, output_items):
        messages = input_items[0]
        codewords = output_items[0]

        # A sync block may be handed many vectors at once. The previous
        # revision encoded only the first and claimed to have produced all of
        # them, so every extra vector went out as an unrelated codeword.
        for i in range(len(codewords)):
            codeword = self.encoder.encode(messages[i].tobytes())
            codewords[i][:] = np.frombuffer(codeword, dtype=np.uint8)

        return len(codewords)
