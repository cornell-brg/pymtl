#=======================================================================
# verilog_from_ast_test.py
#=======================================================================
# This is the test case that verifies the dynamic AST support of PyMTL.
# This test is contributed by Zhuanhao Wu through #169, #170 of PyMTL v2.
#
# Author : Zhuanhao Wu, Peitian Pan
# Date   : Jan 23, 2019

import pytest
import random

from ast import *
from pymtl import *
from pclib.test import run_test_vector_sim
from verilator_sim import TranslationTool

pytestmark = requires_verilator

class ASTRTLModel(Model):
    def __init__( s ):
        s.a = InPort(2)
        s.b = InPort(2)

        s.out = OutPort(2)

        # a simple clocked adder
        # @s.posedge_clk
        # def logic():
        #     s.out.next = s.a + s.b

        # generate the model from ast
        tree = Module(body=[
            FunctionDef(name='logic', args=arguments(args=[], defaults=[]), 
                body= [
                    Assign(targets=[
                        Attribute(value=Attribute(value=Name(id='s', ctx=Load()), attr='out', ctx=Load()), attr='next', ctx=Store())
                        ], 
                        value=BinOp(left=Attribute(value=Name(id='s', ctx=Load()), attr='a', ctx=Load()), op=Add(), right=Attribute(value=Name(id='s', ctx=Load()), attr='b', ctx=Load()))
                        )
                    ],
                decorator_list=[
                    Attribute(value=Name(id='s', ctx=Load()), attr='posedge_clk', ctx=Load())
                    ],
                returns=None)
            ])
        tree = fix_missing_locations(tree)

        # Specifiy the union of globals() and locals() so the free
        # variables in the closure can be captured.
        exec(compile(tree, filename='<ast>', mode='exec')) in globals().update( locals() )

        # As with #175, the user needs to supplement the dynamic AST to
        # the .ast field of the generated function object. 
        logic.ast = tree

def test_ast_rtl_model_works_in_simulation():
    mod = ASTRTLModel()

    test_vector_table = [('a', 'b', 'out*')]
    last_result = '?'
    for i in xrange(3):
        rv1 = Bits(2, random.randint(0, 3))
        rv2 = Bits(2, random.randint(0, 3))
        test_vector_table.append( [ rv1, rv2, last_result ] )
        last_result = Bits(2, rv1 + rv2)

    run_test_vector_sim(mod, test_vector_table)

def test_ast_rtl_model_to_verilog():
    mod = ASTRTLModel()
    # TranslationTool should successfully compile ASTRTLModel
    tool = TranslationTool(mod)
