#=========================================================================
# Local Autoconf Macros
#=========================================================================
# This file contains the macros for the Maven Assembly Test Programs. It
# is derrived from the Modular C++ Build System, so reading the
# documenation in 'tmod-doc.txt' may be helpful. Instead of
# subprojects we use the concept of test modules.

#-------------------------------------------------------------------------
# TMOD_INIT
#-------------------------------------------------------------------------
# Setup any global configure command line arguments and the primary
# running shell variables which will be substituted into the makefile.

AC_DEFUN([TMOD_INIT],
[
  # Running variables to substitute into make
  AC_SUBST([tmod_include])
])

#-------------------------------------------------------------------------
# TMOD_PROG_INSTALL
#-------------------------------------------------------------------------
# This macro will add an --enable-stow command line option to the
# configure script. When enabled, this macro will first check to see if
# the stow program is available and if so it will set the $stow shell
# variable to the binary name and the $enable_stow shell variable to
# "yes". These variables can be used in a makefile to conditionally use
# stow for installation.
#
# This macro uses two environment variables to help setup default stow
# locations. The $STOW_PREFIX is used for stowing native built packages.
# The packages are staged in $STOW_PREFIX/pkgs and then symlinks are
# created from within $STOW_PREFIX into the pkgs subdirectory. If you
# only do native builds then this is all you need to set. If you don't
# set $STOW_PREFIX then the default is just the normal default prefix
# which is almost always /usr/local.
#
# For non-native builds we probably want to install the packages in a
# different location which includes the host architecture name as part
# of the prefix. For these kind of builds, we can specify the $STOW_ROOT
# environment variable and the effective prefix will be
# $STOW_ROOT/${host_alias} where ${host_alias} is specified on the
# configure command line with "--host".
#
# Here is an example setup:
#
#  STOW_ROOT="$HOME/install"
#  STOW_ARCH="i386-macosx10.4"
#  STOW_PREFIX="${STOW_ROOT}/${STOW_ARCH}"
#

AC_DEFUN([TMOD_PROG_INSTALL],
[

  # Configure command line option

  AC_ARG_ENABLE(stow,
    AS_HELP_STRING(--enable-stow,[Enable stow-based install]),
      [enable_stow="yes"],[enable_stow="no"])

  AC_SUBST([enable_stow])

  # Environment variables

  AC_ARG_VAR([STOW_ROOT],   [Root for non-native stow-based installs])
  AC_ARG_VAR([STOW_PREFIX], [Prefix for stow-based installs])

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

    # Check if native or non-native build

    AS_IF([ test "${build}" = "${host}" ],
    [

      # build == host so this is a native build. Make sure --prefix not
      # set and $STOW_PREFIX is set, then set prefix=$STOW_PREFIX.

      AS_IF([ test "${prefix}" = "NONE" && test -n "${STOW_PREFIX}" ],
      [
        prefix="${STOW_PREFIX}"
        AC_MSG_NOTICE([Using \$STOW_PREFIX from environment])
        AC_MSG_NOTICE([prefix=${prefix}])
      ])

    ],[

      # build != host so this is a non-native build. Make sure --prefix
      # not set and $STOW_ROOT is set, then set
      # prefix=$STOW_ROOT/${host_alias}.

      AS_IF([ test "${prefix}" = "NONE" && test -n "${STOW_ROOT}" ],
      [
        prefix="${STOW_ROOT}/${host_alias}"
        AC_MSG_NOTICE([Using \$STOW_ROOT from environment])
        AC_MSG_NOTICE([prefix=${prefix}])
      ])

    ])

  ])

])

#-------------------------------------------------------------------------
# TMOD_PROG_RUN
#-------------------------------------------------------------------------
# If we are doing a non-native build then we look for an isa simulator
# to use for running tests. We set the RUN substitution variable to be
# empty for native builds or to the name of the isa simulator for
# non-native builds. Thus a makefile can run compiled programs
# regardless if we are doing a native or non-native build like this:
#
#  $(RUN) $(RUNFLAGS) ./test-program
#

AC_DEFUN([TMOD_PROG_RUN],
[
  AS_IF([ test "${build}" != "${host}" ],
  [
    AC_CHECK_TOOLS([RUN],[isa-testrun testrun],[no])
    AS_IF([ test ${RUN} = "no" ],
    [
      AC_MSG_ERROR([Cannot find simulator for target ${target_alias}])
    ])
  ],[
    RUN=""
  ])
  AC_SUBST([RUN])
  AC_SUBST([RUNFLAGS])
])

#-------------------------------------------------------------------------
# TMOD_INCLUDE([tmod])
#-------------------------------------------------------------------------

m4_define([TMOD_INCLUDE],
[
  m4_define([TMOD_SPROJ],  m4_bpatsubst(m4_normalize($1),[*],[]))
  m4_define([TMOD_SPROJU], m4_bpatsubst(TMOD_SPROJ,[-],[_]))

  AS_VAR_APPEND([tmod_include],"TMOD_SPROJ ")
])

