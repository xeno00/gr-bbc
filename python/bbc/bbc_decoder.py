#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from collections import deque

import numpy as np
import pmt
from gnuradio import gr

from .codec import Decoder, DEFAULT_CHECKSUM_BITS, DEFAULT_CHECKSUM_MODE


class bbc_decoder(gr.basic_block):
    """BBC decoder: codeword vectors in, decoded message vectors out.

    One codeword may carry zero, one, or several messages, so the block cannot
    be a sync or interpolator block -- those must produce a rate fixed at
    construction time.  It is a basic block with an internal queue instead:
    codewords are consumed as room appears on the output, and decoded messages
    are drained from the queue.

    Each decoded message is also published on the ``decoded`` message port as a
    PMT u8vector, which is usually the easiest way to get the payload out to a
    Message Debug block or to Python.
    """

    def __init__(self, message_length=2**7, codeword_length=2**17,
                 checksum_length=DEFAULT_CHECKSUM_BITS,
                 max_candidates=Decoder.DEFAULT_MAX_CANDIDATES,
                 max_steps=Decoder.DEFAULT_MAX_STEPS,
                 checksum_mode=DEFAULT_CHECKSUM_MODE):
        message_length = int(message_length)
        codeword_length = int(codeword_length)

        gr.basic_block.__init__(
            self,
            name="BBC Decoder",
            in_sig=[(np.uint8, codeword_length)],
            out_sig=[(np.uint8, message_length)])

        self.decoder = Decoder(message_length, codeword_length,
                               int(checksum_length), int(max_candidates),
                               int(max_steps), checksum_mode)
        self.pending = deque()

        self.message_port_name = pmt.intern("decoded")
        self.message_port_register_out(self.message_port_name)

    def forecast(self, noutput_items, ninputs):
        # Queued messages can be emitted without reading anything, so demanding
        # an input codeword here would stall the flowgraph at the end of a
        # stream. Ask for one codeword only when the queue has run dry.
        required = 0 if self.pending else 1
        return [required] * ninputs

    def _decode(self, codeword):
        messages = self.decoder.decode(codeword.tobytes())

        if self.decoder.truncated:
            # Hitting a limit means the codeword is jammed past the point where
            # the search is affordable. Say so rather than silently returning a
            # partial answer.
            self.logger.warn(
                "BBC decode truncated after %d steps and %d candidates; the "
                "codeword is likely saturated with marks"
                % (self.decoder.steps, len(messages)))

        for message in messages:
            self.pending.append(np.frombuffer(message, dtype=np.uint8))
            self.message_port_pub(
                self.message_port_name,
                pmt.cons(pmt.PMT_NIL,
                         pmt.init_u8vector(len(message), list(message))))

    def general_work(self, input_items, output_items):
        codewords = input_items[0]
        messages = output_items[0]
        capacity = len(messages)

        consumed = 0
        while len(self.pending) < capacity and consumed < len(codewords):
            self._decode(codewords[consumed])
            consumed += 1
        if consumed:
            self.consume(0, consumed)

        produced = 0
        while produced < capacity and self.pending:
            messages[produced][:] = self.pending.popleft()
            produced += 1

        return produced
