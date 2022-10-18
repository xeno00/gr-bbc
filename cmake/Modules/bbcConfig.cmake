INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_BBC bbc)

FIND_PATH(
    BBC_INCLUDE_DIRS
    NAMES bbc/api.h
    HINTS $ENV{BBC_DIR}/include
        ${PC_BBC_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    BBC_LIBRARIES
    NAMES gnuradio-bbc
    HINTS $ENV{BBC_DIR}/lib
        ${PC_BBC_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/bbcTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(BBC DEFAULT_MSG BBC_LIBRARIES BBC_INCLUDE_DIRS)
MARK_AS_ADVANCED(BBC_LIBRARIES BBC_INCLUDE_DIRS)
