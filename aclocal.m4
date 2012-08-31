#=========================================================================
# Local Autoconf Macros
#=========================================================================
# This file contains the macros for the Modular Python Build System and
# additional autoconf macros which developers can use in their
# configure.ac scripts.The documenation for each macro should include
# information about the author, date, and copyright.

#-------------------------------------------------------------------------
# MPBS_PROG_INSTALL
#-------------------------------------------------------------------------
# This macro will add an --enable-stow command line option to the
# configure script. When enabled, this macro will first check to see if
# the stow program is available and if so it will set the $stow shell
# variable to the binary name and the $enable_stow shell variable to
# "yes". These variables can be used in a makefile to conditionally use
# stow for installation.
#
# This macro uses two environment variables to help setup default stow
# locations. The $STOW_PKGS_PREFIX is used for stowing native built
# packages. The packages are staged in $STOW_PKGS_PREFIX/pkgs and then
# symlinks are created from within $STOW_PKGS_PREFIX into the pkgs
# subdirectory. If you don't set $STOW_PKGS_PREFIX then the default is
# just the normal default prefix which is almost always /usr/local.
#
# Here is an example setup:
#
#  ARCH="i386-macosx10.4"
#  STOW_PKGS_ROOT="${HOME}/install/stow-pkgs"
#  STOW_PKGS_PREFIX="${STOW_PKGS_ROOT}/${ARCH}"
#

AC_DEFUN([MPBS_PROG_INSTALL],
[

  # Configure command line option

  AC_ARG_ENABLE(stow,
    AS_HELP_STRING(--enable-stow,[Enable stow-based install]),
      [enable_stow="yes"],[enable_stow="no"])

  AC_SUBST([enable_stow])

  # Environment variables

  AC_ARG_VAR([STOW_PKGS_ROOT],   [Root for non-native stow-based installs])
  AC_ARG_VAR([STOW_PKGS_PREFIX], [Prefix for stow-based installs])

  # Check for install script

  AC_PROG_INSTALL

  # Deterimine if native build and set prefix appropriately

  AS_IF([ test "${enable_stow}" = "yes" ],
  [
    AC_CHECK_PROGS([stow],[stow],[no])
    AS_IF([ test "${stow}" = "no" ],
    [
      AC_MSG_ERROR([Cannot use --enable-stow since stow is not available])
    ])

    # Make sure --prefix not set and $STOW_PKGS_PREFIX is set, then set
    # prefix=$STOW_PKGS_PREFIX.

    AS_IF([ test "${prefix}" = "NONE" && test -n "${STOW_PKGS_PREFIX}" ],
    [
      prefix="${STOW_PKGS_PREFIX}"
      AC_MSG_NOTICE([Using \$STOW_PKGS_PREFIX from environment])
      AC_MSG_NOTICE([prefix=${prefix}])
    ])

  ])

])

#-------------------------------------------------------------------------
# MPBS_PROG_PYTHON
#-------------------------------------------------------------------------
# Checks to make sure that python is in users path otherwise the
# configuration fails.

AC_DEFUN([MPBS_PROG_PYTHON],
[
  AC_CHECK_PROGS([python],[python],[no])
  AS_IF([test $python = "no"],
  [
    AC_MSG_ERROR([Modular Python Build System requires python])
  ])
])

#-------------------------------------------------------------------------
# MPBS_PROG_PYTEST
#-------------------------------------------------------------------------
# Checks to make sure that py.test is in users path otherwise the
# configuration fails.

AC_DEFUN([MPBS_PROG_PYTEST],
[
  AC_CHECK_PROGS([pytest],[py.test],[no])
  AS_IF([test $pytest = "no"],
  [
    AC_MSG_ERROR([Modular Python Build System requires py.test])
  ])
])

#-------------------------------------------------------------------------
# AX_COMPARE_VERSION( VER_A, OP, VER_B, [IF-TRUE], [IF-FALSE] )
#-------------------------------------------------------------------------
# This macro compares two version strings. Due to the various number of
# minor-version numbers that can exist, and the fact that string
# comparisons are not compatible with numeric comparisons, this is not
# necessarily trivial to do in a autoconf script. This macro makes doing
# these comparisons easy.
#
# The six basic comparisons are available, as well as checking equality
# limited to a certain number of minor-version levels.
#
# The operator OP determines what type of comparison to do, and can be
# one of:
#
#  eq  - equal (test A == B)
#  ne  - not equal (test A != B)
#  le  - less than or equal (test A <= B)
#  ge  - greater than or equal (test A >= B)
#  lt  - less than (test A < B)
#  gt  - greater than (test A > B)
#
# Additionally, the eq and ne operator can have a number after it to
# limit the test to that number of minor versions.
#
#  eq0 - equal up to the length of the shorter version
#  ne0 - not equal up to the length of the shorter version
#  eqN - equal up to N sub-version levels
#  neN - not equal up to N sub-version levels
#
# When the condition is true, shell commands ACTION-IF-TRUE are run,
# otherwise shell commands ACTION-IF-FALSE are run. The environment
# variable 'ax_compare_version' is always set to either 'true' or
# 'false' as well.
#
# Examples:
#
#   AX_COMPARE_VERSION([3.15.7],[lt],[3.15.8])
#   AX_COMPARE_VERSION([3.15],[lt],[3.15.8])
#
# would both be true.
#
#   AX_COMPARE_VERSION([3.15.7],[eq],[3.15.8])
#   AX_COMPARE_VERSION([3.15],[gt],[3.15.8])
#
# would both be false.
#
#   AX_COMPARE_VERSION([3.15.7],[eq2],[3.15.8])
#
# would be true because it is only comparing two minor versions.
#
#   AX_COMPARE_VERSION([3.15.7],[eq0],[3.15])
#
# would be true because it is only comparing the lesser number of minor
# versions of the two values.
#
# Note: The characters that separate the version numbers do not matter.
# An empty string is the same as version 0. OP is evaluated by autoconf,
# not configure, so must be a string, not a variable.
#
# The author would like to acknowledge Guido Draheim whose advice about
# the m4_case and m4_ifvaln functions make this macro only include the
# portions necessary to perform the specific comparison specified by the
# OP argument in the final configure script.
#
# Author : Tim Toolan <toolan@ele.uri.edu>
# Date   : 2008
# Web    : http://www.nongnu.org/autoconf-archive/ax_compare_version.html
#
# Copyright (c) 2008 Tim Toolan <toolan@ele.uri.edu>
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.

AC_DEFUN([AX_COMPARE_VERSION],
[
  AC_REQUIRE([AC_PROG_AWK])

  # Used to indicate true or false condition
  ax_compare_version=false

  # Convert the two version strings to be compared into a format that
  # allows a simple string comparison. The end result is that a version
  # string of the form 1.12.5-r617 will be converted to the form
  # 0001001200050617. In other words, each number is zero padded to four
  # digits, and non digits are removed.
  AS_VAR_PUSHDEF([A],[ax_compare_version_A])
  A=`echo "$1" | sed -e 's/\([[0-9]]*\)/Z\1Z/g' \
                     -e 's/Z\([[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/[[^0-9]]//g'`

  AS_VAR_PUSHDEF([B],[ax_compare_version_B])
  B=`echo "$3" | sed -e 's/\([[0-9]]*\)/Z\1Z/g' \
                     -e 's/Z\([[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/Z\([[0-9]][[0-9]][[0-9]]\)Z/Z0\1Z/g' \
                     -e 's/[[^0-9]]//g'`

  dnl In the case of le, ge, lt, and gt, the strings are sorted as
  dnl necessary then the first line is used to determine if the
  dnl condition is true. The sed right after the echo is to remove any
  dnl indented white space.

  m4_case(m4_tolower($2),
  [lt],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort -r | sed "s/x${A}/false/;s/x${B}/true/;1q"`
  ],
  [gt],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort | sed "s/x${A}/false/;s/x${B}/true/;1q"`
  ],
  [le],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort | sed "s/x${A}/true/;s/x${B}/false/;1q"`
  ],
  [ge],[
    ax_compare_version=`echo "x$A
x$B" | sed 's/^ *//' | sort -r | sed "s/x${A}/true/;s/x${B}/false/;1q"`
  ],[
    dnl Split the operator from the subversion count if present.
    m4_bmatch(m4_substr($2,2),
    [0],[
      # A count of zero means use the length of the shorter version.
      # Determine the number of characters in A and B.
      ax_compare_version_len_A=`echo "$A" | $AWK '{print(length)}'`
      ax_compare_version_len_B=`echo "$B" | $AWK '{print(length)}'`

      # Set A to no more than B's len and B to no more than A's len.
      A=`echo "$A" | sed "s/\(.\{$ax_compare_version_len_B\}\).*/\1/"`
      B=`echo "$B" | sed "s/\(.\{$ax_compare_version_len_A\}\).*/\1/"`
    ],
    [[0-9]+],[
      # A count greater than zero means use only that many subversions
      A=`echo "$A" | sed "s/\(\([[0-9]]\{4\}\)\{m4_substr($2,2)\}\).*/\1/"`
      B=`echo "$B" | sed "s/\(\([[0-9]]\{4\}\)\{m4_substr($2,2)\}\).*/\1/"`
    ],
    [.+],[
      AC_WARNING(
        [illegal OP numeric parameter: $2])
    ],[])

    # Pad zeros at end of numbers to make same length.
    ax_compare_version_tmp_A="$A`echo $B | sed 's/./0/g'`"
    B="$B`echo $A | sed 's/./0/g'`"
    A="$ax_compare_version_tmp_A"

    # Check for equality or inequality as necessary.
    m4_case(m4_tolower(m4_substr($2,0,2)),
    [eq],[
      test "x$A" = "x$B" && ax_compare_version=true
    ],
    [ne],[
      test "x$A" != "x$B" && ax_compare_version=true
    ],[
      AC_WARNING([illegal OP parameter: $2])
    ])
  ])

  AS_VAR_POPDEF([A])dnl
  AS_VAR_POPDEF([B])dnl

  dnl # Execute ACTION-IF-TRUE / ACTION-IF-FALSE.
  if test "$ax_compare_version" = "true" ; then
    m4_ifvaln([$4],[$4],[:])dnl
    m4_ifvaln([$5],[else $5])dnl
  fi

])

