//******************************************************************************
// Copyright 2015 Cadence Design Systems, Inc.
// All Rights Reserved.
//
//******************************************************************************
#ifdef SYSTEMC_SIM
#include "systemc-sim.h"
#elif defined STRATUS_HLS
#include "systemc-stratus-hls.h"
#else
#include "systemc.h"
#endif

#ifndef _DEFINES_H_
#define _DEFINES_H_

typedef sc_biguint<160> RoccCmdMsg;
typedef sc_biguint<69>  RoccRespMsg;
typedef sc_biguint<77>  MemReqMsg;
typedef sc_uint<47>  MemRespMsg;

#endif


