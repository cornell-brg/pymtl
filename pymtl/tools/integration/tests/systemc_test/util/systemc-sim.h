//========================================================================
// systemc-sim.h
//========================================================================
// This header is used for systemc simulation purpose. That is, all
// Stratus HLS macros are defined as empty things here to unify the code
// for HLS and simulation

#ifndef _SYSTEMC_SIM_H_
#define _SYSTEMC_SIM_H_

#include "systemc.h"

#define HLS_DEFINE_PROTOCOL(...)
#define HLS_ASSUME_STABLE(...)
#define HLS_BREAK_PROTOCOL(...)
#define HLS_COALESCE_LOOP(...)
#define HLS_CONSTRAIN_ARRAY_MAX_DISTANCE(...)
#define HLS_CONSTRAIN_LATENCY(...)
#define HLS_CONSTRAIN_REGION(...)
#define HLS_DEFINE_FLOATING_PROTOCOL(...)
#define HLS_DEFINE_PROTOCOL(...)
#define HLS_DEFINE_STALL_LOOP(...)
#define HLS_DPOPT_REGION(...)
#define HLS_EXPOSE_PORT(...)
#define HLS_FLATTEN_ARRAY(...)
#define HLS_INITIALIZE_ROM(...)
#define HLS_INLINE_MODULE(...)
#define HLS_INVERT_DIMENSIONS(...)
#define HLS_MAP_ARRAY_INDEXES(...)
#define HLS_MAP_TO_MEMORY(...)
#define HLS_MAP_TO_REG_BANK(...)
#define HLS_METAPORT(...)
#define HLS_NAME(...)
#define HLS_PIPELINE_LOOP(...)
#define HLS_PRESERVE_IO_SIGNALS(...)
#define HLS_PRESERVE_SIGNAL(...)
#define HLS_REMOVE_CONTROL(...)
#define HLS_SCHEDULE_REGION(...)
#define HLS_SEPARATE_ARRAY(...)
#define HLS_SET_CLOCK_PERIOD(...)
#define HLS_SET_CYCLE_SLACK(...)
#define HLS_SET_DEFAULT_INPUT_DELAY(...)
#define HLS_SET_DEFAULT_OUTPUT_DELAY(...)
#define HLS_SET_DEFAULT_OUTPUT_OPTIONS(...)
#define HLS_SET_INPUT_DELAY(...)
#define HLS_SET_IS_BOUNDED(...)
#define HLS_SET_OUTPUT_DELAY(...)
#define HLS_SET_OUTPUT_OPTIONS(...)
#define HLS_SET_STALL_VALUE(...)
#define HLS_UNROLL_LOOP(...)

#endif /* _SYSTEMC_SIM_H_ */
