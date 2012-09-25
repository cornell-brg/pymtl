#=========================================================================
# Toplevel configure.ac for the Modular C++ Build System
#=========================================================================
# Please read the documenation in 'mcppbs-doc.txt' for more details on
# how the Modular C++ Build System works. For most new projects, a
# developer will only need to change the project metadata listed right
# below, and update which subprojects to include as part of this
# project. Do not place any configure checks here which will be used by
# a subproject - instead place such checks in the subproject's autoconf
# fragment.

#-------------------------------------------------------------------------
# Project metadata
#-------------------------------------------------------------------------

m4_define( proj_name,         [PARC Assembly Test Programs])
m4_define( proj_maintainer,   [Ji Kim])
m4_define( proj_abbreviation, [parc-test])

#-------------------------------------------------------------------------
# Project version information
#-------------------------------------------------------------------------
# Version information is meant to be managed through a version control
# system's tags and revision numbers. In a working copy the version will
# not be defined here (you should just use the version control system's
# mechanisms). When we make a distribution then we can set the version
# here as formed by the scripts/vcs-version.sh script so that the
# distribution knows what version it came from. If you are not using
# version control then it is fine to set this directly.

m4_define( proj_version, [?])

#-------------------------------------------------------------------------
# Setup
#-------------------------------------------------------------------------

AC_INIT(proj_name,proj_version,proj_maintainer,proj_abbreviation)
AC_CONFIG_SRCDIR([scripts/test.ld])
AC_CONFIG_AUX_DIR([scripts])
AC_CANONICAL_BUILD
AC_CANONICAL_HOST

#-------------------------------------------------------------------------
# Basic checks
#-------------------------------------------------------------------------

# Check for C compiler and set default C compiler flags
AC_PROG_CC
AC_SUBST([CFLAGS],["-Wall"])

#-------------------------------------------------------------------------
# TMOD specific setup
#-------------------------------------------------------------------------

# Initialize the build system

TMOD_INIT

# Check for install script and the stow proram.
TMOD_PROG_INSTALL

# Check for an isa simulator.
TMOD_PROG_RUN

#-------------------------------------------------------------------------
# TMOD includes
#-------------------------------------------------------------------------
# Specify which test modules to include

TMOD_INCLUDE([parcv1])
TMOD_INCLUDE([parcv2])
#TMOD_INCLUDE([parcv3])
#TMOD_INCLUDE([simt])
#TMOD_INCLUDE([amo])

#-------------------------------------------------------------------------
# Output
#-------------------------------------------------------------------------

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
