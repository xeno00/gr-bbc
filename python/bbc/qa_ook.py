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

from gnuradio import gr, gr_unittest, blocks

if __package__ in (None, ''):
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bbc.OOKModulator import OOKModulator
from bbc.OOKDemodulator import OOKDemodulator

SAMP_RATE = 128e3
SYMBOL_RATE = 500
CARRIER = 20e3


class qa_ook(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instantiate(self):
        self.assertIsNotNone(OOKModulator(CARRIER, SAMP_RATE, SYMBOL_RATE))
        self.assertIsNotNone(OOKDemodulator(CARRIER, SAMP_RATE, SYMBOL_RATE))

    def test_sample_rate_below_symbol_rate_is_rejected(self):
        self.assertRaises(ValueError, OOKModulator, CARRIER, 100, 500)
        self.assertRaises(ValueError, OOKDemodulator, CARRIER, 100, 500)

    def test_modulator_output_is_gated_by_input(self):
        """All-zero bytes must key the carrier off, all-ones must key it on."""
        sps = int(SAMP_RATE / SYMBOL_RATE)
        for payload, expect_energy in (([0] * 8, False), ([0xFF] * 8, True)):
            tb = gr.top_block()
            src = blocks.vector_source_b(payload, False)
            mod = OOKModulator(CARRIER, SAMP_RATE, SYMBOL_RATE)
            sink = blocks.vector_sink_c()
            tb.connect(src, mod, sink)
            tb.run()

            data = sink.data()
            self.assertEqual(len(data), len(payload) * 8 * sps)
            energy = sum(abs(x) ** 2 for x in data) / len(data)
            if expect_energy:
                self.assertGreater(energy, 0.1)
            else:
                self.assertLess(energy, 1e-9)

    def test_alignment_skip(self):
        """The sampler must discard exactly the band-pass group delay."""
        self.assertEqual(OOKDemodulator._alignment_skip(77), 38)
        self.assertEqual(OOKDemodulator._alignment_skip(617), 308)
        self.assertEqual(OOKDemodulator._alignment_skip(1), 0)

    def _loopback_bits(self, core, carrier=CARRIER, demod_carrier=None,
                       **kwargs):
        """Modulate `core`, demodulate it, return the received bit string.

        Tail padding covers the filter warm-up the demodulator discards, so the
        whole payload survives.
        """
        payload = list(core) + [0x00] * 4
        src = blocks.vector_source_b(payload, False)
        mod = OOKModulator(carrier, SAMP_RATE, SYMBOL_RATE)
        demod = OOKDemodulator(
            carrier if demod_carrier is None else demod_carrier,
            SAMP_RATE, SYMBOL_RATE, **kwargs)
        sink = blocks.vector_sink_b()
        self.tb.connect(src, mod, demod, sink)
        self.tb.run()
        return ''.join(format(b & 0xFF, '08b') for b in sink.data())

    def test_loopback_is_bit_transparent(self):
        """Demodulated bit j must be modulated bit j, with no offset.

        Flowgraphs slice the demodulated stream straight back into codeword
        vectors, so a constant offset of even one symbol breaks decoding.
        """
        core = [0xFF, 0xA5, 0x5A, 0x01, 0x80, 0x3C, 0xC3, 0x7E]
        recv = self._loopback_bits(core)
        sent = ''.join(format(b, '08b') for b in core)
        self.assertTrue(
            recv.startswith(sent),
            "demodulated stream is offset from the modulated stream:\n"
            "  sent %s\n  recv %s" % (sent, recv[:len(sent)]))

    def test_bit_transparency_holds_across_carriers(self):
        core = [0xA5, 0x5A, 0x3C, 0x81]
        sent = ''.join(format(b, '08b') for b in core)
        for carrier in (10e3, 20e3, 30e3, 45e3):
            self.tb = gr.top_block()
            self.assertTrue(
                self._loopback_bits(core, carrier=carrier).startswith(sent),
                "carrier %g Hz is not bit transparent" % carrier)

    def test_loopback_survives_noise(self):
        """BBC needs marks preserved; check the slicer holds up under AWGN."""
        from gnuradio import analog

        core = [0xFF, 0xA5, 0x5A, 0x3C]
        pad = [0x00] * 4
        payload = pad + core + pad

        src = blocks.vector_source_b(payload, False)
        mod = OOKModulator(CARRIER, SAMP_RATE, SYMBOL_RATE)
        noise = analog.noise_source_c(analog.GR_GAUSSIAN, 0.2, 7)
        adder = blocks.add_cc()
        demod = OOKDemodulator(CARRIER, SAMP_RATE, SYMBOL_RATE)
        sink = blocks.vector_sink_b()

        self.tb.connect(src, mod, (adder, 0))
        self.tb.connect(noise, (adder, 1))
        self.tb.connect(adder, demod, sink)
        self.tb.run()

        recv = ''.join(format(b & 0xFF, '08b') for b in sink.data())
        self.assertIn(''.join(format(b, '08b') for b in core), recv)

    def test_band_pass_rejects_off_channel_carrier(self):
        """A signal on another channel must not survive the band-pass."""
        core = [0xFF] * 4
        self.assertIn('1' * 32, self._loopback_bits(core))

        # Same signal, demodulator tuned 40 kHz away.
        self.tb = gr.top_block()
        self.assertNotIn(
            '1' * 32,
            self._loopback_bits(core, demod_carrier=CARRIER + 40e3))


if __name__ == '__main__':
    unittest.main()
