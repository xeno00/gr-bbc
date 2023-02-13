# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: OOK Modulator
# Author: James Morrison
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal







class OOKModulator(gr.hier_block2):
    def __init__(self, carrier_freq=433.937e6, samp_rate=128e3, symbol_rate=int (500)):
        gr.hier_block2.__init__(
            self, "OOK Modulator",
                gr.io_signature(1, 1, gr.sizeof_char*1),
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.carrier_freq = carrier_freq
        self.samp_rate = samp_rate
        self.symbol_rate = symbol_rate

        ##################################################
        # Variables
        ##################################################
        self.bits_per_pack = bits_per_pack = 8

        ##################################################
        # Blocks
        ##################################################
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(bits_per_pack)
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_float*1, int(samp_rate / symbol_rate))
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, carrier_freq, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_uchar_to_float_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.blocks_uchar_to_float_0, 0))
        self.connect((self, 0), (self.blocks_unpack_k_bits_bb_0, 0))


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
        self.blocks_repeat_0.set_interpolation(int(self.samp_rate / self.symbol_rate))

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.blocks_repeat_0.set_interpolation(int(self.samp_rate / self.symbol_rate))

    def get_bits_per_pack(self):
        return self.bits_per_pack

    def set_bits_per_pack(self, bits_per_pack):
        self.bits_per_pack = bits_per_pack

