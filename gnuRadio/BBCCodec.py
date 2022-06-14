#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BBCCodec
# Author: James Morrison
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

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
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
import epy_block_0_0
import epy_block_2
from gnuradio import qtgui

class BBCCodec(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "BBCCodec")
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

        self.settings = Qt.QSettings("GNU Radio", "BBCCodec")

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
        self.samp_rate = samp_rate = 1024*2
        self.codeword = codeword = "HELLOWORLD"

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_char, 1, "tcp://127.0.0.1:5557", 100, False, -1)
        self.epy_block_2 = epy_block_2.blk(example_param=1.0)
        self.epy_block_2.set_block_alias("Encode")
        self.epy_block_0_0 = epy_block_0_0.blk(output_chunk_size=len(codeword), dbug=1)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1, 2**20)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([ord(i) for i in codeword], True, 1, [])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_stream_to_vector_decimator_0 = blocks.stream_to_vector_decimator(
            item_size=gr.sizeof_char,
            sample_rate=samp_rate,
            vec_rate=samp_rate/2,
            vec_len=2**10)
        self.blocks_stream_to_vector_decimator_0.set_block_alias("Message")
        self.blocks_message_debug_0 = blocks.message_debug()



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0_0, 'msgs'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.blocks_stream_to_vector_decimator_0, 0), (self.epy_block_2, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_decimator_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.epy_block_0_0, 0))
        self.connect((self.epy_block_0_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.epy_block_2, 0), (self.blocks_vector_to_stream_1, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "BBCCodec")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_stream_to_vector_decimator_0.set_sample_rate(self.samp_rate)
        self.blocks_stream_to_vector_decimator_0.set_vec_rate(self.samp_rate/2)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_codeword(self):
        return self.codeword

    def set_codeword(self, codeword):
        self.codeword = codeword
        self.blocks_vector_source_x_0_0.set_data([ord(i) for i in self.codeword], [])
        self.epy_block_0_0.output_chunk_size = len(self.codeword)



def main(top_block_cls=BBCCodec, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
