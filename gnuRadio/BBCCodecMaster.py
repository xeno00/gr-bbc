#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: BBCCodec
# Author: James Morrison
# GNU Radio version: 3.9.5.0

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
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import BBCCodecMaster_epy_block_0 as epy_block_0  # embedded python block
import BBCCodecMaster_epy_block_2 as epy_block_2  # embedded python block



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
        self.codeword = codeword = "HELLOWORLD"
        self.MESSAGE_LENGTH = MESSAGE_LENGTH = 2**10
        self.CODEWORD_LENGTH = CODEWORD_LENGTH = 2**20

        ##################################################
        # Blocks
        ##################################################
        self.epy_block_2 = epy_block_2.blk(msg_len=MESSAGE_LENGTH, cod_len=CODEWORD_LENGTH)
        self.epy_block_0 = epy_block_0.blk(msg_len=MESSAGE_LENGTH, cod_len=CODEWORD_LENGTH)
        self.blocks_vector_to_stream_1_0 = blocks.vector_to_stream(gr.sizeof_char*1, 2**10)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1, 2**20)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([ord(i) for i in codeword], True, 1, [])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, 32000,True)
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_char*1, '', "")
        self.blocks_tag_debug_0.set_display(True)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_char*1, 2**20)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 1024)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'testOutput.txt', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self.epy_block_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_vector_to_stream_1_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_vector_to_stream_1_0, 0))
        self.connect((self.epy_block_2, 0), (self.blocks_vector_to_stream_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "BBCCodecMaster")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_codeword(self):
        return self.codeword

    def set_codeword(self, codeword):
        self.codeword = codeword
        self.blocks_vector_source_x_0_0.set_data([ord(i) for i in self.codeword], [])

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
