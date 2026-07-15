# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

include(GrPython)

gr_python_install(
    FILES
        __init__.py
        bbc_decoder.py
        bbc_encoder.py
        codec.py
        ook_demodulator.py
        ook_modulator.py
    DESTINATION ${GR_PYTHON_DIR}/gnuradio/bbc
)
