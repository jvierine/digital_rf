#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.
#
#  Digital RF configure.ac file
#
#  Written by Bill Rideout (brideout@haystack.mit.edu)
#
#  $Id: configure.ac 1022 2016-03-14 21:26:16Z rvolz $

AC_PREREQ(2.59)
AC_INIT([Digital_rf], [1.1.3], [brideout@haystack.mit.edu])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADER([config.h])

AM_PROG_AR
# Checks for programs.
AC_PROG_CC
AC_PROG_LIBTOOL

# Checks and defines HDF5 library using macro
AX_LIB_HDF5()
if test "$with_hdf5" = "no"; then
    AC_MSG_ERROR([Hdf5 C library must be installed first.  See http://www.hdfgroup.org/HDF5/])
fi

# distribute additional compiler and linker flags among Makefiles
# --> set and change these variables instead of CPPFLAGS or LDFLAGS (for user only)
AC_SUBST([AM_CPPFLAGS])
AC_SUBST([AM_LDFLAGS])

# files to generate via autotools (prepare .am or .in source files)
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([source/Makefile])

# finally this generates the Makefiles etc. for the build
AC_OUTPUT
