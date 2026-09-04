# Copyright 2011 Free Software Foundation, Inc.
#
# This file is a part of gr-bbc
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Include python install macros
########################################################################
include(GrPython)
if(NOT PYTHONINTERP_FOUND)
    return()
endif()

########################################################################
# Install python sources
########################################################################
# gr-bbc is pure Python, so there are no pybind11 bindings to add here.
gr_python_install(
    FILES __init__.py
          codec.py
          glowworm.py
          bbc_encoder.py
          bbc_decoder.py
          OOKDemodulator.py
          OOKModulator.py
    DESTINATION ${GR_PYTHON_DIR}/bbc)

########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

# Create a package directory the tests can import, mirroring `python/bbc/`.
add_custom_target(
    copy_module_for_tests ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}
            ${PROJECT_BINARY_DIR}/test_modules/bbc/)

set(GR_TEST_PYTHON_DIRS ${PROJECT_BINARY_DIR}/test_modules)

list(APPEND GR_TEST_PYTHON_FILES qa_codec.py qa_bbc_encoder.py
     qa_bbc_decoder.py qa_ook.py)

foreach(qa_file IN LISTS GR_TEST_PYTHON_FILES)
    gr_add_test(${qa_file} ${QA_PYTHON_EXECUTABLE} -B
                ${CMAKE_CURRENT_SOURCE_DIR}/${qa_file})
endforeach()
