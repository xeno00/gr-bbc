#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Stream to Vector Test
# Author: Neil Rogers
# GNU Radio version: v3.8.2.0-57-gd71cd177

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq


class stream2vec_test(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Stream to Vector Test")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.codeword = codeword = "HELLOWORLD"
        self.addy = addy = "tcp://127.0.0.1:5557"

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, len(codeword), addy, 100, False, -1)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([ord(i) for i in codeword], True, 1, [])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, 32000,True)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, len(codeword))
        self.blocks_head_0 = blocks.head(gr.sizeof_char*10, 10)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_head_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_head_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_throttle_0, 0))


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_codeword(self):
        return self.codeword

    def set_codeword(self, codeword):
        self.codeword = codeword
        self.blocks_vector_source_x_0_0.set_data([ord(i) for i in self.codeword], [])

    def get_addy(self):
        return self.addy

    def set_addy(self, addy):
        self.addy = addy





def main(top_block_cls=stream2vec_test, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
