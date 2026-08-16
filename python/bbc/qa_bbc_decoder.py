#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import os
import sys
import unittest

import numpy as np
import pmt
from gnuradio import gr, gr_unittest, blocks

if __package__ in (None, ''):
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bbc.bbc_encoder import bbc_encoder
from bbc.bbc_decoder import bbc_decoder

MSG_LEN = 8
COD_LEN = 2**12


class qa_bbc_decoder(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def _loopback(self, messages, checksum_length=32):
        """Encode then decode `messages` through a real flowgraph."""
        payload = b"".join(messages)
        src = blocks.vector_source_b(list(payload), False, MSG_LEN)
        enc = bbc_encoder(MSG_LEN, COD_LEN, checksum_length)
        dec = bbc_decoder(MSG_LEN, COD_LEN, checksum_length)
        sink = blocks.vector_sink_b(MSG_LEN)
        debug = blocks.message_debug()

        self.tb.connect(src, enc, dec, sink)
        self.tb.msg_connect((dec, 'decoded'), (debug, 'store'))
        self.tb.run()

        flat = np.array(sink.data(), dtype=np.uint8)
        stream = [bytes(v) for v in flat.reshape(-1, MSG_LEN)]
        msgs = [bytes(pmt.u8vector_elements(pmt.cdr(debug.get_message(i))))
                for i in range(debug.num_messages())]
        return stream, msgs

    def test_instantiate(self):
        self.assertIsNotNone(bbc_decoder(MSG_LEN, COD_LEN))

    def test_single_message_round_trip(self):
        stream, msgs = self._loopback([b"GRCon26!"])
        self.assertEqual(stream, [b"GRCon26!"])
        self.assertEqual(msgs, [b"GRCon26!"])

    def test_many_messages_round_trip(self):
        # Reusing one decoder across packets used to leave the search index at
        # -1, so every message after the first was lost.
        messages = [bytes([i]) * MSG_LEN for i in range(32)]
        stream, msgs = self._loopback(messages)
        self.assertEqual(stream, messages)
        self.assertEqual(msgs, messages)

    def test_round_trip_without_checksum(self):
        messages = [b"nochksum", b"stillok!"]
        stream, _ = self._loopback(messages, checksum_length=0)
        self.assertEqual(stream, messages)

    def test_all_zero_codeword_yields_nothing(self):
        # An empty channel must not stall the flowgraph or emit junk.
        src = blocks.vector_source_b([0] * (COD_LEN * 4), False, COD_LEN)
        dec = bbc_decoder(MSG_LEN, COD_LEN)
        sink = blocks.vector_sink_b(MSG_LEN)
        self.tb.connect(src, dec, sink)
        self.tb.run()
        self.assertEqual(sink.data(), [])

    def test_saturated_codeword_does_not_wedge_the_flowgraph(self):
        # Every branch looks plausible when all marks are set. The block must
        # hit its limits, log, and keep running rather than search forever.
        src = blocks.vector_source_b([0xFF] * (COD_LEN * 2), False, COD_LEN)
        dec = bbc_decoder(MSG_LEN, COD_LEN, 0,
                          max_candidates=8, max_steps=20000)
        sink = blocks.vector_sink_b(MSG_LEN)
        self.tb.connect(src, dec, sink)
        self.tb.run()
        self.assertTrue(dec.decoder.truncated)
        self.assertEqual(len(sink.data()) // MSG_LEN, 16)

    def test_concurrent_messages_in_one_codeword(self):
        # Two codewords OR'd together: BBC's defining property.
        a, b = b"message1", b"message2"
        src_a = blocks.vector_source_b(list(a), False, MSG_LEN)
        src_b = blocks.vector_source_b(list(b), False, MSG_LEN)
        enc_a = bbc_encoder(MSG_LEN, COD_LEN)
        enc_b = bbc_encoder(MSG_LEN, COD_LEN)
        combine = blocks.or_bb()
        v2s_a = blocks.vector_to_stream(gr.sizeof_char, COD_LEN)
        v2s_b = blocks.vector_to_stream(gr.sizeof_char, COD_LEN)
        s2v = blocks.stream_to_vector(gr.sizeof_char, COD_LEN)
        dec = bbc_decoder(MSG_LEN, COD_LEN)
        sink = blocks.vector_sink_b(MSG_LEN)

        self.tb.connect(src_a, enc_a, v2s_a, (combine, 0))
        self.tb.connect(src_b, enc_b, v2s_b, (combine, 1))
        self.tb.connect(combine, s2v, dec, sink)
        self.tb.run()

        flat = np.array(sink.data(), dtype=np.uint8)
        decoded = [bytes(v) for v in flat.reshape(-1, MSG_LEN)]
        self.assertCountEqual(decoded, [a, b])


if __name__ == '__main__':
    unittest.main()
