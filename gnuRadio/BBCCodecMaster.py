#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BBCCodec
# Author: James Morrison
# GNU Radio version: 3.10.3.0

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import BBCCodecMaster_epy_block_0 as epy_block_0  # embedded python block
import BBCCodecMaster_epy_block_2 as epy_block_2  # embedded python block
import BBCCodecMaster_epy_block_2_0 as epy_block_2_0  # embedded python block



from gnuradio import qtgui

class BBCCodecMaster(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "BBCCodec", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("BBCCodec")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "BBCCodecMaster")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.message2 = message2 = "ZELLO ZORLD! Zelcome zo ZBC zn ZNURadio. Zhis zs z zam-zesistant zodec, znd ze zre zending zessages, zncoding zhem, znd zhen zry"
        self.message1 = message1 = "HELLO WORLD! Welcome to BBC in GNURadio. This is a jam-resistant codec, and we are sending messages, encoding them, and then try"
        self.MESSAGE_LENGTH = MESSAGE_LENGTH = 128
        self.CODEWORD_LENGTH = CODEWORD_LENGTH = 131072

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, 1, "tcp://127.0.0.1:5557", 100, False, (-1))
        self.epy_block_2_0 = epy_block_2_0.blk()
        self.epy_block_2 = epy_block_2.blk()
        self.epy_block_0 = epy_block_0.blk()
        self.blocks_vector_to_stream_1_1 = blocks.vector_to_stream(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_vector_to_stream_1_0 = blocks.vector_to_stream(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_vector_source_x_0_0_0 = blocks.vector_source_b([ord(i) for i in message2], False, 1, [])
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([ord(i) for i in message1], False, 1, [])
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_char*1, 32000,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, 32000,True)
        self.blocks_tag_debug_0_0 = blocks.tag_debug(gr.sizeof_char*1, '', "")
        self.blocks_tag_debug_0_0.set_display(True)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_char*1, '', "")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_char*1, CODEWORD_LENGTH)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, MESSAGE_LENGTH)
        self.blocks_or_xx_0 = blocks.or_bb()


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_or_xx_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.epy_block_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.epy_block_2_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.blocks_tag_debug_0_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_vector_source_x_0_0_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_or_xx_0, 1))
        self.connect((self.blocks_vector_to_stream_1_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.blocks_vector_to_stream_1_1, 0), (self.blocks_or_xx_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_vector_to_stream_1_0, 0))
        self.connect((self.epy_block_2, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.epy_block_2_0, 0), (self.blocks_vector_to_stream_1_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "BBCCodecMaster")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_message2(self):
        return self.message2

    def set_message2(self, message2):
        self.message2 = message2
        self.blocks_vector_source_x_0_0_0.set_data([ord(i) for i in self.message2], [])

    def get_message1(self):
        return self.message1

    def set_message1(self, message1):
        self.message1 = message1
        self.blocks_vector_source_x_0_0.set_data([ord(i) for i in self.message1], [])

    def get_MESSAGE_LENGTH(self):
        return self.MESSAGE_LENGTH

    def set_MESSAGE_LENGTH(self, MESSAGE_LENGTH):
        self.MESSAGE_LENGTH = MESSAGE_LENGTH

    def get_CODEWORD_LENGTH(self):
        return self.CODEWORD_LENGTH

    def set_CODEWORD_LENGTH(self, CODEWORD_LENGTH):
        self.CODEWORD_LENGTH = CODEWORD_LENGTH




def main(top_block_cls=BBCCodecMaster, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
