# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

try:
    from gnuradio import blocks, gr
    import bbc
except ModuleNotFoundError:
    blocks = None
    gr = None
    bbc = None


@unittest.skipUnless(gr is not None, "GNU Radio is not installed")
class GNUradioBlockTests(unittest.TestCase):
    def test_codec_flowgraph_round_trip(self):
        message = [ord("A")]
        flowgraph = gr.top_block()
        source = blocks.vector_source_b(message, False)
        to_vector = blocks.stream_to_vector(gr.sizeof_char, 1)
        encoder = bbc.bbc_encoder(1, 64)
        decoder = bbc.bbc_decoder(1, 64)
        to_stream = blocks.vector_to_stream(gr.sizeof_char, 1)
        sink = blocks.vector_sink_b()

        flowgraph.connect(source, to_vector, encoder, decoder, to_stream, sink)
        flowgraph.run()

        self.assertIn(ord("A"), sink.data())

    def test_ook_loopback(self):
        flowgraph = gr.top_block()
        source = blocks.vector_source_b([0xA5], False)
        modulator = bbc.OOKModulator(0.0, 8_000, 1_000)
        demodulator = bbc.OOKDemodulator(8_000, 1_000, 0.5)
        head = blocks.head(gr.sizeof_char, 1)
        sink = blocks.vector_sink_b()

        flowgraph.connect(source, modulator, demodulator, head, sink)
        flowgraph.run()

        self.assertEqual(sink.data(), (0xA5,))


if __name__ == "__main__":
    unittest.main()
