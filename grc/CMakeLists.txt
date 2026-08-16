# Copyright 2011 Free Software Foundation, Inc.
#
# This file is a part of gr-bbc
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

install(FILES bbc_bbc_encoder.block.yml
              bbc_bbc_decoder.block.yml
              bbc_OOKModulator.block.yml
              bbc_OOKDemodulator.block.yml
        DESTINATION share/gnuradio/grc/blocks)
