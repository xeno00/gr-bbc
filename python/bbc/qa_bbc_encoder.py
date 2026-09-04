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
from gnuradio import gr, gr_unittest, blocks

if __package__ in (None, ''):
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bbc.codec import Encoder
from bbc.bbc_encoder import bbc_encoder

MSG_LEN = 8
COD_LEN = 2**12


class qa_bbc_encoder(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def _run(self, messages):
        payload = b"".join(messages)
        src = blocks.vector_source_b(list(payload), False, MSG_LEN)
        enc = bbc_encoder(MSG_LEN, COD_LEN)
        sink = blocks.vector_sink_b(COD_LEN)
        self.tb.connect(src, enc, sink)
        self.tb.run()
        flat = np.array(sink.data(), dtype=np.uint8)
        return flat.reshape(-1, COD_LEN)

    def test_instantiate(self):
        self.assertIsNotNone(bbc_encoder(MSG_LEN, COD_LEN))

    def test_single_vector_matches_reference(self):
        msg = b"GRCon26!"
        got = self._run([msg])
        expected = np.frombuffer(
            bytes(Encoder(MSG_LEN, COD_LEN).encode(msg)), dtype=np.uint8)
        self.assertEqual(got.shape, (1, COD_LEN))
        np.testing.assert_array_equal(got[0], expected)

    def test_every_vector_is_encoded(self):
        # The old block encoded only the first vector of each work() call but
        # returned the full count, so the rest of the stream was garbage.
        messages = [bytes([i]) * MSG_LEN for i in range(64)]
        got = self._run(messages)
        self.assertEqual(got.shape, (64, COD_LEN))

        reference = Encoder(MSG_LEN, COD_LEN)
        for i, msg in enumerate(messages):
            expected = np.frombuffer(bytes(reference.encode(msg)),
                                     dtype=np.uint8)
            np.testing.assert_array_equal(got[i], expected,
                                          "vector %d differs" % i)

    def test_repeated_message_gives_repeated_codeword(self):
        msg = b"AAAAAAAA"
        got = self._run([msg] * 4)
        for i in range(1, 4):
            np.testing.assert_array_equal(got[0], got[i])


if __name__ == '__main__':
    unittest.main()
