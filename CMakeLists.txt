# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

cmake_minimum_required(VERSION 3.16)
project(gr-bbc VERSION 1.0.0 LANGUAGES C CXX)

set(VERSION_MAJOR 1)
set(VERSION_API 0)
set(VERSION_ABI 0)
set(VERSION_PATCH 0)

include(CTest)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Gnuradio "3.10" REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

include(GrMinReq)
include(GrCompilerSettings)
include(GrPython)
include(GrVersion)
include(GrPlatform)

add_subdirectory(python/bbc)
add_subdirectory(grc)
add_subdirectory(examples)

if(BUILD_TESTING)
    add_test(
        NAME bbc_python_core
        COMMAND
            ${CMAKE_COMMAND} -E env
            "PYTHONPATH=${PROJECT_SOURCE_DIR}/python"
            ${Python3_EXECUTABLE} -m unittest discover
            -s ${PROJECT_SOURCE_DIR}/tests -p test_codec.py -v
    )
    add_test(
        NAME bbc_gnuradio_blocks
        COMMAND
            ${CMAKE_COMMAND} -E env
            "PYTHONPATH=${PROJECT_SOURCE_DIR}/python"
            ${Python3_EXECUTABLE} -m unittest discover
            -s ${PROJECT_SOURCE_DIR}/tests -p test_gnuradio_blocks.py -v
    )
    set_tests_properties(
        bbc_python_core bbc_gnuradio_blocks
        PROPERTIES TIMEOUT 60
    )
endif()

install(
    FILES MANIFEST.yml
    RENAME MANIFEST-${PROJECT_VERSION}.yml
    DESTINATION share/gnuradio/manifests/bbc
)
