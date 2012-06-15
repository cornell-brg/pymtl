from vgen_func import cvalrdy, ivalrdy, ovalrdy, create_module

num_mem_ports = 2

def req_resp_port_def(req_sz, resp_sz, i=0):
  req_pfx = 'memreq%d'  % i
  resp_pfx = 'memresp%d' % i
  ports = []
  ports += ivalrdy(req_pfx, req_sz)
  ports += ovalrdy(resp_pfx, resp_sz)
  return ports

def req_resp_port_ifc(i=0):
  req_pfx = 'memreq'
  resp_pfx = 'memresp'
  req_pfx2= 'memreq%d'  % i
  resp_pfx2= 'memresp%d' % i
  ports = []

  ports += zip(cvalrdy(req_pfx), cvalrdy(req_pfx2))
  ports += zip(cvalrdy(resp_pfx), cvalrdy(resp_pfx2))
  return ports


import StringIO
o = StringIO.StringIO()

def p_inst(params):
  for p,v in params[:-1]:
    print >> o, '    .%s (%s),' % (p,v)
  p,v = params[-1]
  print >> o, '    .%s (%s)' % (p,v)

def instantiate_module(module, inst_name, connections, params=None):
  """connections should take (port, wire) tuples,
     params should take (param, value) tuples.
  """
  # Module Name
  if not params:
    print >> o, '  %s %s' % (module, inst_name)
  else:
    print >> o, '  %s#(' % module
    p_inst(params)
    print >> o, '  )'
    print >> o, '  %s' % inst_name
  print >> o, '  ('
  p_inst(connections)
  print >> o, '  );'

def inst_wires(i):
  print >> o, ('  wire [c_physical_block_addr_sz-1:0] '
               '  physical_block_addr_M%d;' % i)
  print >> o, ('  wire [p_data_sz-1:0]                '
               '  read_block_M%d;' % i)
  print >> o, ('  wire                                '
               '  write_en_M%d;'% i)
  print >> o, ('  wire [c_req_msg_len_sz:0]        '
               '  memreq_msg_len_modified_M%d;' % i)
  print >> o, ('  wire [c_block_offset_sz-1:0]        '
               '  block_offset_M%d;' % i)
  print >> o, ('  wire [c_req_msg_data_sz-1:0]        '
               '  memreq_msg_data_modified_M%d;' % i)
  print >> o, ('  wire                                '
               '  arb_amo_en%d;' % i)
  print >> o

def inst_m_ports(i):
  ports = []
  ports += [('clk', 'clk'), ('reset', 'reset')]
  ports += req_resp_port_ifc(i)
  ports += [('physical_block_addr_M',
             'physical_block_addr_M%d' % i )]
  ports += [('read_block_M',
             'read_block_M%d' % i )]
  ports += [('write_en_M',
             'write_en_M%d' % i )]
  ports += [('memreq_msg_len_modified_M',
             'memreq_msg_len_modified_M%d' % i )]
  ports += [('block_offset_M',
             'block_offset_M%d' % i )]
  ports += [('memreq_msg_data_modified_M',
             'memreq_msg_data_modified_M%d' % i )]
  ports += [('arb_amo_en',
             'arb_amo_en%d' % i )]
  ports += [('amo_grant',
             'amo_grants[%d]' % i )]
  return ports


import sys
def n_port_mem(num_mem_ports, width):
  name = 'vgen_Magic%dPortMem' % num_mem_ports

  # Includes
  print >> sys.stdout, '`include "vc-MemReqMsg.v"'
  print >> sys.stdout, '`include "vc-MemRespMsg.v"'
  print >> sys.stdout, '`include "vc-Assert.v"'
  print >> sys.stdout, '`include "vc-Queues.v"'
  print >> sys.stdout, '`include "vgen-TestMemReqRespPort.v"'
  print >> sys.stdout

  # Define Wires
  for i in range(num_mem_ports):
    inst_wires(i)
  print >> o, ('  wire [%d-1:0]                       '
               '  amo_grants;' % num_mem_ports)
  print >> o

  # Instantiate modules
  for i in range(num_mem_ports):
    iname = 'port%d' % i
    ports = inst_m_ports(i)
    params = []
    params += [('p_mem_sz',  'p_mem_sz')]
    params += [('p_addr_sz', 'p_addr_sz')]
    params += [('p_data_sz', 'p_data_sz')]
    instantiate_module('vc_TestReqRespMemPort', iname, ports, params)


  # Add some other logic
  print >> o
  print >> o, '  reg [p_data_sz-1:0] m[c_num_blocks-1:0];'
  print >> o, '  wire [%d-1:0] amo_reqs;' % num_mem_ports
  print >> o

  for i in range(num_mem_ports):

    print >> o, '  assign amo_reqs[%d] = arb_amo_en%d;' % (i,i)
    print >> o,('  assign read_block_M%d = m[physical_block_addr_M%d];'
                % (i,i))
    print >> o, '  integer wr%d_i;' % i
    print >> o, '  always @( posedge clk ) begin'
    print >> o, '    if ( write_en_M%d ) begin' % i
    print >> o,('      for ( wr%d_i = 0; wr%d_i < memreq_msg_len_modified_M%d;'
                ' wr%d_i = wr%d_i + 1 ) begin' % (i,i,i,i,i))
    print >> o, '       m[physical_block_addr_M%d][ (block_offset_M%d*8) + (wr%d_i*8) +: 8 ]' % (i,i,i)
    print >> o, '         <= memreq_msg_data_modified_M%d[ (wr%d_i*8) +: 8 ];' % (i,i)
    print >> o, '      end'
    print >> o, '    end'
    print >> o, '  end'

  #wire [1:0] amo_reqs = { arb_amo_en1, arb_amo_en0 };

  print >> o
  ports = [('clk','clk'),
           ('reset','reset'),
           ('reqs','amo_reqs'),
           ('grants','amo_grants'),
          ]
  params = [('NUM_REQS', str(num_mem_ports))]
  instantiate_module('vc_RoundRobinArb', 'arb', ports, params=params)


  # Generate top level module
  ports = ['input clk', 'input reset']
  for i in range(num_mem_ports):
    ports += req_resp_port_def('c_req_msg_sz','c_resp_msg_sz', i)
  params = []
  params += [('p_mem_sz', '1024')]
  params += [('p_addr_sz', '16')]
  params += [('p_data_sz', str(width))]
  params += [('c_req_msg_sz', '`VC_MEM_REQ_MSG_SZ(p_addr_sz,p_data_sz)')]
  params += [('c_resp_msg_sz', '`VC_MEM_RESP_MSG_SZ(p_data_sz)')]
  params += [('c_data_byte_sz', 'p_data_sz/8')]
  params += [('c_num_blocks','p_mem_sz/c_data_byte_sz')]
  params += [('c_physical_block_addr_sz', '$clog2(c_num_blocks)')]
  params += [('c_block_offset_sz', '$clog2(c_data_byte_sz)')]
  params += [('c_req_msg_len_sz',
             '`VC_MEM_REQ_MSG_LEN_SZ(p_addr_sz,p_data_sz)')]
  params += [('c_req_msg_data_sz',
              '`VC_MEM_REQ_MSG_DATA_SZ(p_addr_sz,p_data_sz)')]

  create_module(name, o, ports,params=params)

n_port_mem(4,  16)
#n_port_mem(10,  8)
