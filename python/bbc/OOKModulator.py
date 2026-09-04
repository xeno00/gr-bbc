#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""On-off keying modulator for BBC codewords.

Packed bytes in, complex baseband out.  Each byte is unpacked MSB first, held
for ``samp_rate / symbol_rate`` samples, and used to gate a complex carrier.

``carrier_freq`` is an offset within the baseband spectrum, so keep
``abs(carrier_freq) < samp_rate / 2`` -- anything above Nyquist aliases back to
some other offset rather than raising an error.
"""

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr

BITS_PER_BYTE = 8


class OOKModulator(gr.hier_block2):

    def __init__(self, carrier_freq=20e3, samp_rate=128e3, symbol_rate=500):
        gr.hier_block2.__init__(
            self, "OOK Modulator",
            gr.io_signature(1, 1, gr.sizeof_char * 1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex * 1),
        )

        self.carrier_freq = carrier_freq
        self.samp_rate = samp_rate
        self.symbol_rate = symbol_rate

        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(
            BITS_PER_BYTE)
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_repeat_0 = blocks.repeat(
            gr.sizeof_float * 1, self._samples_per_symbol())
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(
            samp_rate, analog.GR_COS_WAVE, carrier_freq, 1, 0, 0)

        self.connect((self, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0),
                     (self.blocks_uchar_to_float_0, 0))
        self.connect((self.blocks_uchar_to_float_0, 0),
                     (self.blocks_repeat_0, 0))
        self.connect((self.blocks_repeat_0, 0),
                     (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0),
                     (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0),
                     (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self, 0))

    def _samples_per_symbol(self):
        sps = int(self.samp_rate / self.symbol_rate)
        if sps < 1:
            raise ValueError(
                "samp_rate (%g) must be at least symbol_rate (%g)"
                % (self.samp_rate, self.symbol_rate))
        return sps

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.analog_sig_source_x_0.set_frequency(self.carrier_freq)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.blocks_repeat_0.set_interpolation(self._samples_per_symbol())

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.blocks_repeat_0.set_interpolation(self._samples_per_symbol())
