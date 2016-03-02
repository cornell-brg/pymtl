#=======================================================================
# Model_dummy_test.py
#=======================================================================
# Dummy classes for verifying the valid construction and elaboration of
# models.

from Model import Model

# Used in test case "ClassNameCollision"
class ClassNameCollisionModel( Model ):
  def __init__( s, arg1, arg2 ):
    s.arg1 = arg1
    s.arg2 = arg2

