//******************************************************************************
// Copyright 2015 Cadence Design Systems, Inc.
// All Rights Reserved.
//
//******************************************************************************


#include "VvaddXcelSC.h"

RoccCmdMsg VvaddXcelSC::xcelreq_get()
{
  //SC_DEFINE_PROTOCOL("xcelreq_get");
  
  xcelreq_rdy.write(1);
  do { wait(); } while (xcelreq_val.read()==0);
  xcelreq_rdy.write(0);
  
  //cout<<sc_time_stamp()<<" [xcel] get req"<<endl;
  return xcelreq_msg.read();
}
void VvaddXcelSC::xcelresp_put(const RoccRespMsg &msg)
{
  //SC_DEFINE_PROTOCOL("xcelresp_put");
  //cout<<sc_time_stamp()<<" [xcel] put resp"<<endl;
  
  xcelresp_msg.write(msg);
  xcelresp_val.write(1);
  do { wait(); } while (xcelresp_rdy.read()==0);
  xcelresp_val.write(0);
}
MemRespMsg VvaddXcelSC::memresp_get()
{
  //SC_DEFINE_PROTOCOL("memresp_get");
  
  memresp_rdy.write(1);
  do { wait(); } while (memresp_val.read()==0);
  memresp_rdy.write(0);
  
  return memresp_msg.read();
}
void VvaddXcelSC::memreq_put(const MemReqMsg &msg)
{
  //SC_DEFINE_PROTOCOL("memreq_put");
  
  memreq_msg.write(msg);
  memreq_val.write(1);
  do { wait(); } while (memreq_rdy.read()==0);
  memreq_val.write(0);
}

void VvaddXcelSC::configure()
{
  while (1)
  {
    RoccCmdMsg req = xcelreq_get();
    sc_uint<7>  type = RoccCmd_type(req);
    sc_uint<5>  xreg = RoccCmd_xreg(req);
    sc_uint<64> data = RoccCmd_data(req);
    
    if (type == _rd_) break;
    
    xr[xreg] = data;  
    xcelresp_put(RoccResp(0));
  }
}

void VvaddXcelSC::finalize()
{
  xcelresp_put(1);
}

void VvaddXcelSC::xcel_work()
{
  {
    //SC_DEFINE_PROTOCOL("reset");
    
    // We must put the reset signal here,
    // otherwise the reset block is not registered.
    // For example, if we put this piece of code into configure()
    // The module won't be reset properly
    
    printf("VvaddXcelSC: got reset signal\n");
    
    xcelresp_msg.write(0);
    xcelresp_val.write(false);
    xcelreq_rdy.write(false);
    memreq_msg.write(0);
    memreq_val.write(false);
    memresp_rdy.write(false);
    wait();
  }
  
  // We have to put a infinite loop here to keep the accelerator alive.
  // If we don't put a infinite loop, the reset signal is not able 
  // to reset the module, since after the first execution the xcel_work 
  // method has already finished.
  
  while (1)
  {
    configure();
    
    for (unsigned i=0;i<xr[4]<<2;i+=4)
    {
      MemReqMsg req = MemReq(_rd_, xr[1]+i, 0);
      memreq_put(req);
      unsigned a = MemResp_data(memresp_get());
    
      req = MemReq(_rd_, xr[2]+i, 0);
      memreq_put(req);
      unsigned b = MemResp_data(memresp_get());

      req = MemReq(_wr_, xr[3]+i, a+b);
      memreq_put(req);
      memresp_get();
    }
    
    finalize();
  }
}
