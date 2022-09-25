#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BBCCodec
# Author: James Morrison
# GNU Radio version: 3.10.3.0

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import BBCCodecMaster_epy_block_0 as epy_block_0  # embedded python block
import BBCCodecMaster_epy_block_2 as epy_block_2  # embedded python block
import BBCCodecMaster_epy_block_2_0 as epy_block_2_0  # embedded python block




class BBCCodecMaster(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "BBCCodec", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.message2 = message2 = "ZELLO ZORLD! Zelcome zo ZBC zn ZNURadio. Zhis zs z zam-zesistant zodec, znd ze zre zending zessages, zncoding zhem, znd zhen zry"
        self.message1 = message1 = "HELLO WORLD! Welcome to BBC in GNURadio. This is a jam-resistant codec, and we are sending messages, encoding them, and then try"
        self.MESSAGE_LENGTH = MESSAGE_LENGTH = 128
        self.CODEWORD_LENGTH = CODEWORD_LENGTH = 1024

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, 1, "tcp://127.0.0.1:5555", 100, False, (-1))
        self.epy_block_2_0 = epy_block_2_0.blk()
        self.epy_block_2 = epy_block_2.blk()
        self.epy_block_0 = epy_block_0.blk()
        self.blocks_vector_to_stream_1_1 = blocks.vector_to_stream(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_vector_to_stream_1_0 = blocks.vector_to_stream(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_vector_source_x_0_0_0 = blocks.vector_source_b([ord(i) for i in message1], True, 1, [])
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([ord(i) for i in message2], False, 1, [])
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_char*1, 32000,True)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_or_xx_0 = blocks.or_bb()
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_char*1)
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_message_debug_1 = blocks.message_debug(True)
        self.blocks_head_0_0 = blocks.head(gr.sizeof_char*1, (int(MESSAGE_LENGTH*2)))
        self.blocks_head_0 = blocks.head(gr.sizeof_char*1, (int(MESSAGE_LENGTH*2)))


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'msgOutput'), (self.blocks_message_debug_1, 'print'))
        self.connect((self.blocks_head_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.blocks_head_0_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_or_xx_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.epy_block_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.epy_block_2_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_head_0_0, 0))
        self.connect((self.blocks_vector_source_x_0_0_0, 0), (self.blocks_head_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_or_xx_0, 1))
        self.connect((self.blocks_vector_to_stream_1_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.blocks_vector_to_stream_1_1, 0), (self.blocks_or_xx_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_vector_to_stream_1_0, 0))
        self.connect((self.epy_block_2, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.epy_block_2_0, 0), (self.blocks_vector_to_stream_1_1, 0))


    def get_message2(self):
        return self.message2

    def set_message2(self, message2):
        self.message2 = message2
        self.blocks_vector_source_x_0_0.set_data([ord(i) for i in self.message2], [])

    def get_message1(self):
        return self.message1

    def set_message1(self, message1):
        self.message1 = message1
        self.blocks_vector_source_x_0_0_0.set_data([ord(i) for i in self.message1], [])

    def get_MESSAGE_LENGTH(self):
        return self.MESSAGE_LENGTH

    def set_MESSAGE_LENGTH(self, MESSAGE_LENGTH):
        self.MESSAGE_LENGTH = MESSAGE_LENGTH
        self.blocks_head_0.set_length((int(self.MESSAGE_LENGTH*2)))
        self.blocks_head_0_0.set_length((int(self.MESSAGE_LENGTH*2)))

    def get_CODEWORD_LENGTH(self):
        return self.CODEWORD_LENGTH

    def set_CODEWORD_LENGTH(self, CODEWORD_LENGTH):
        self.CODEWORD_LENGTH = CODEWORD_LENGTH




def main(top_block_cls=BBCCodecMaster, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
