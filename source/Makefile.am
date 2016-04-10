# $Id: Makefile.am 1022 2016-03-14 21:26:16Z rvolz $
#
# Makefile.am for Digital RF
#
# Written by Bill Rideout (brideout@haystack.mit.edu)

ACLOCAL_AMFLAGS = -I m4

AM_CPPFLAGS = $(HDF5_CPPFLAGS)
AM_LDFLAGS = $(HDF5_LDFLAGS)

include_HEADERS = digital_rf.h

lib_LTLIBRARIES = libdigital_rf.la

libdigital_rf_la_SOURCES = rf_write_hdf5.c

LDADD = -ldigital_rf

# test programs only
check_PROGRAMS = test_rf_write_hdf5 benchmark_rf_write_hdf5 example_rf_write_hdf5

