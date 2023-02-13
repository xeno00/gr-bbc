# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: OOK Demodulator
# Author: James Morrison
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal







class OOKDemodulator(gr.hier_block2):
    def __init__(self, samp_rate=128e3, symbol_rate=500):
        gr.hier_block2.__init__(
            self, "OOK Demodulator",
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
                gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.samp_rate = samp_rate
        self.symbol_rate = symbol_rate

        ##################################################
        # Blocks
        ##################################################
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(1e-3, 1e-3, 0)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*1, int(samp_rate / symbol_rate))
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.band_pass_filter_0 = filter.fir_filter_ccc(
            1,
            firdes.complex_band_pass(
                1,
                samp_rate,
                1,
                50e3,
                20e3,
                window.WIN_HAMMING,
                6.76))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self, 0))
        self.connect((self, 0), (self.band_pass_filter_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, 1, 50e3, 20e3, window.WIN_HAMMING, 6.76))
        self.blocks_keep_one_in_n_0.set_n(int(self.samp_rate / self.symbol_rate))

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.blocks_keep_one_in_n_0.set_n(int(self.samp_rate / self.symbol_rate))

