# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/ben/esp-idf-v5.3.1/components/bootloader/subproject"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/tmp"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/src/bootloader-stamp"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/src"
  "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/ben/Documents/bozzio/CarCanSimulator/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
