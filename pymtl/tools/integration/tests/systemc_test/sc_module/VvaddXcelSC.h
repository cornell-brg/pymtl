#ifndef _VVADDXCELSC_H_
#define _VVADDXCELSC_H_

#include "defines.h"
#include "msgs.h"

SC_MODULE(VvaddXcelSC)
{
public:
  sc_in<bool> clk;
  sc_in<bool> rst;
  
  // proc ports
  sc_in <RoccCmdMsg > xcelreq_msg;
  sc_in <bool       > xcelreq_val;
  sc_out<bool       > xcelreq_rdy;
  
  sc_out<RoccRespMsg> xcelresp_msg;
  sc_out<bool       > xcelresp_val;
  sc_in <bool       > xcelresp_rdy;
  
  // mem ports
  sc_out<MemReqMsg > memreq_msg;
  sc_out<bool      > memreq_val;
  sc_in <bool      > memreq_rdy;
  
  sc_in <MemRespMsg> memresp_msg;
  sc_in <bool      > memresp_val;
  sc_out<bool      > memresp_rdy;
  
  /*
   * xr0 : go
   * xr1 : A[]
   * xr2 : B[]
   * xr3 : C[]
   * xr4 : N
   */
  sc_uint<64> xr[5];
  
  // loop variable, for line_trace
  unsigned i;
  
  SC_CTOR(VvaddXcelSC)
  {
    SC_CTHREAD(xcel_work, clk.pos());
    reset_signal_is(rst,1);
  }
  
  /* this method is called upon posedge clock */
  void xcel_work();
  
  /* 
   * these two methods are to make xcel_work look concise
   * -- XcelWrapper in pymtl-polyhs
   */
  void configure();
  void finalize();
  
  /* 
   * helper methods that wrap the val/rdy protocol
   * into get/put transactions
   */
  RoccCmdMsg xcelreq_get();
  void xcelresp_put(const RoccRespMsg &msg);
  
  MemRespMsg memresp_get();
  void memreq_put(const MemReqMsg &msg);
  
  void line_trace(char *str);
};

#endif
