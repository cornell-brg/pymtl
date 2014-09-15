# Test start assembly fragment

asm_start = """
    .text;
    .align  4;
    .global _test;
    .ent    _test;
_test:
"""

# Test end assembly fragment

asm_end = """
_pass:
    addiu  $29, $0, 1;

_fail:
    li     $2,  1;
    mtc0   $29, $21;
1:  bne    $0, $2, 1b;
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
    nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;

    .end _test
"""

def asm_force_fail( reg_, value_ ):
  return asm_start + """

    li    $29, 1111;
    bne   $29, $0, _fail;

  """.format( **locals() ) + asm_end


def genasm_test_imm_op( inst, src0, imm, result ):
    return asm_start + """

      li      $2, {src0};
      {inst}  $4, $2, {imm};
      li     $29, 1111;
      bne     $4, {result}, _fail

    """.format( **locals() ) + asm_end

def genasm_test_rr_op( inst, src0, src1, result ):
    return asm_start + """

    li      $2, {src0};
    li      $3, {src1};
    {inst}  $4, $2, $3;
    li     $29, 1111;
    bne     $4, {result}, _fail

    """.format( **locals() ) + asm_end

def genasm_test_lui_op( inst, imm, result ):
    return asm_start + """

      li      $2, 0;
      {inst}  $2, {imm};
      li     $29, 1111;
      bne     $2, {result}, _fail

    """.format( **locals() ) + asm_end

def genasm_test_ld_op( inst, offset, base, result ):
    return asm_start + """

      la      $2, {base};
      {inst}  $4, {offset}($2);
      li     $29, 1111;
      bne     $4, {result}, _fail

    """.format( **locals() ) + asm_end

def genasm_test_sw_op( inst, wdata, offset, base, result ):
    return asm_start + """

      la      $2, {base};
      li      $3, {wdata};
      {inst}  $3, {offset}($2);
      lw      $4, {offset}($2);
      li     $29, 1111;
      bne     $4, {result}, _fail

    """.format( **locals() ) + asm_end

def genasm_test_br2_op( inst, src0, src1, taken=True ):
    result = 1 if taken else 2
    return asm_start + """

      li      $4, 0;
      li      $2, {src0};
      li      $3, {src1};
      {inst}  $3, $2, 2f;
      addiu   $4, $4, 1;
1:    addiu   $4, $4, 1;
      bne     $4, $0, 3f;
2:    {inst}  $3, $2, 1b;
3:    li     $29, 1111;
      bne     $4, {result}, _fail

    """.format( **locals() ) + asm_end
