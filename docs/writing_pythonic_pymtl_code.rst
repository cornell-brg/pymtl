===============================================================================
Writing Pythonic PyMTL Models and Tests
===============================================================================

This document contains a list of tips for writing PyMTL code in a "Pythonic"
way. Some of these recommendations address style and syntax changes in the
PyMTL framework as it has evolved over time, while others are more applicable
to Python programming in general.

Note that some of our style suggestions do differ considerably from standard
Python practices. This is particularly true of PyMTL Models which are written
in the PyMTL embedded-DSL. I've tried to design the embedded-DSL to be
"Pythonic" where possible yet sufficiently distinct to suggest to users that
they are designing hardware, not software. Certain style tradeoffs have been
made to make the embedded-DSL a more familiar hardware description language:

- Brevity has been chosen over clarity in some cases to better resemble the
  syntax of HDLs like Verilog.
- Style-limitations are imposed on RTL models to support Verilog translation.

Also keep in mind that PyMTL is a vertically-integrated design framework meant
for describing models at various levels of abstraction. Functional-level (FL)
models have no translation restrictions on their behavioral blocks and can
leverage the full-power of constructs provided by the Python language; they
should aim to stylistically follow Python best-practices where possible.
However, behavioral blocks in RTL models must abide by translation restrictions
and may potentially look far less "Pythonic".

-------------------------------------------------------------------------------
Table of Contents
-------------------------------------------------------------------------------

- `Use "s" for models, use "self" for classes`_
- `Do not define an "elaborate_logic" method`_
- `Do not use ".value" for signals on the right-hand side of expressions`_
- `Prefer "range()" over "xrange()"`_
- `Use "_" when "range()" index is unused`_
- `Prefer "enumerate()" and "zip()" over "len()"`_
- `Prefer "randrange()" over "randint()"`_

-------------------------------------------------------------------------------
Use "s" for models, use "self" for classes
-------------------------------------------------------------------------------

Python classes typically use ``self`` as the name of the first argument in
method definitions to refer to the object instance parameter. However, this is
simply a (good) naming convention and the user can use any name they want if
they so choose (however, they should generally always choose ``self``!).

In PyMTL, we've adopted the following convention for the naming of the first
argument of method definitions:

- Use ``s`` when writing PyMTL models
  (a.k.a. Python classes which subclass from Model)
- Use ``self`` when writing PyMTL classes for any other purpose
  (e.g. utility classes, tools, testing libraries, and core components)

This naming convention serves the dual purpose of 1) distinguishing Models
written using the PyMTL embedded-DSL from normal Python classes and 2)
providing a more concise, HDL-like syntax when writing RTL in PyMTL::

  # A user-defined utility class. Uses self in method definitions.
  class MyPythonUtilityClass( object ):

    def __init__( self, a, b ):
      self.a = a
      self.b = a

    def some_calc( self, in ):
      return self.a * self.b + in

  # A user-defined PyMTL model. Uses s in method definitions.
  class MyPyMTLModel( Model ):

    def __init__( s, a, b ):
      s.in_ = InPort ( 16 )
      s.out = OutPort( 33 )

      @s.tick_fl
      def logic():
        s.out.next = a * b + s.in_

-------------------------------------------------------------------------------
Do not define an "elaborate_logic" method
-------------------------------------------------------------------------------

Previous versions of the PyMTL framework used ``__init__`` for defining the
model's Port-based interface and a separate ``elaborate_logic()`` method for
implementing static elaboration. This resulted in excessive boiler-plate when
static elaboration steps depended on construction parameters that had to be
saved and restored::

  class OldStyleModel( Model ):

    # Define the port based interface in __init__.
    def __init__( s, dtype, shift_value ):

      s.in_ = InPort ( dtype )
      s.out = OutPort( dtype )

      # Storing parameter values needed in static elaboration.
      # This gets annoying with many parameters!
      s.shift_value = shiftvalue

    # Define static elaboration in elaborate_logic.
    def elaborate_logic( s ):

      @s.combinational
      def logic():
        # Use the stored parameter in our logic.
        s.out.value = s.in_ << s.shift_value

Instead, PyMTL models should just define an ``__init__`` method which specifies
both the interface and static elaboration. While this provides a less explicit
separation between interface definitions and static elaboration code, it
significantly reduces boilerplate::

  class NewStyleModel( Model ):

    # Define the port based interface and static elaboration in __init__.
    def __init__( s, dtype, shift_value ):

      s.in_ = InPort ( dtype )
      s.out = OutPort( dtype )

      @s.combinational
      def logic():
        # Use the parameter in our logic.
        s.out.value = s.in_ << shift_value

-------------------------------------------------------------------------------
Do not use ".value" for signals on the right-hand side of expressions
-------------------------------------------------------------------------------

Previous versions of the PyMTL framework required accessing the ``.value``
attribute in order to both write **and** read the data transported over
InPorts, OutPorts, and Wires. This resulted in fairly verbose PyMTL code::

  class And3( Model ):
    def __init__( s ):
      s.in0 = InPort ( 1 )
      s.in1 = InPort ( 1 )
      s.in2 = InPort ( 1 )
      s.out = OutPort( 1 )

      @s.combinational
      def logic():
        s.out.value = s.in0.value and s.in1.value and s.in2.value

Current versions of the PyMTL framework only require the use of ``.value`` when
writing the value of an InPort, OutPort, or Wire, not when reading. While
reading ``.value`` is still behaviorally valid, code is much more concise and
readable when it is left off::

  class And3( Model ):
    def __init__( s ):
      s.in0 = InPort ( 1 )
      s.in1 = InPort ( 1 )
      s.in2 = InPort ( 1 )
      s.out = OutPort( 1 )

      @s.combinational
      def logic():
        s.out.value = s.in0 and s.in1 and s.in2

-------------------------------------------------------------------------------
Prefer "range()" over "xrange()"
-------------------------------------------------------------------------------

Python2.7 provides two functions which are commonly used for defining the
bounds of for loops and list comprehensions: ``range()`` and ``xrange``. These
methods can generally be used interchangeably, however ``range()`` returns a
list whereas ``xrange()`` returns a generator. Because ``xrange()`` produces
values on demand, it's recommended for use when creating extremely large
arrays.

In Python3 and above, ``xrange()`` has been removed and ``range()`` adopts the
behavior of ``xrange()``. While PyMTL currently only supports Python2.7, for
the purpose of future portability we recommend only using ``range()`` where
possible. This should typically not be a problem unless iterating through
extremely large datasets.

-------------------------------------------------------------------------------
Use "_" when "range()" index is unused
-------------------------------------------------------------------------------

In PyMTL, it's fairly common to create lists of components using a list
comprehension where the index variable is unused. In this scenario, use "_"
rather than "x" or "i" as the range variable as a hint to users that the index
is unused::

  def okay_create_module_list( s, size, params_list ):
    s.submods = [ MyModule( *params_list ) for x in range( size ) ]

  def better_create_module_list( s, size, params_list ):
    s.submods = [ MyModule( *params_list ) for _ in range( size ) ]

When the module is a signal (InPort, OutPort, Wire) or a PyMTL model (subclass
of Model), you can use the even more concise list constructor syntax::

  def best_create_module_list( s, size, params_list ):
    s.submods = MyModel[ size ]( *params_list )

Using "_" rather than a named index variable also applies to for loops::

  def unused_enumerate_variable( dest, src0, src1 ):

    # using zip would be even cleaner!
    for i, _ in enumrate( dest ):
      dest[i] = src0[i] + src1[i]


-------------------------------------------------------------------------------
Prefer "enumerate()" and "zip()" over "len()"
-------------------------------------------------------------------------------

Programmers coming from C-like languages will often write for loops in the
following way::

  for i in range( len(data) ):
    print '{} {}'.format( i, data[i] )

This can be written much more cleanly using ``enumerate()``, which returns both
the index number and current iterator item::

  for i, item in enumerate( data ):
    print '{} {}'.format( i, data )

Loops which use ``range()`` can be often be written more cleanly using the
``zip()`` method, which returns items from multiple iterators in lock-step::

  def okay_all_done():
    is_done = 1
    for i in range( len(s.srcs) ):
      is_done &= (s.srcs[i].done and s.sinks[i].done)
    return is_done

  def better_all_done():
    is_done = 1
    for src, sink in zip( s.srcs, s.sinks ):
      is_done &= (src.done and sink.done)
    return is_done

Note that ``zip()`` and ``enumerate()`` are not Verilog translatable, so
``range()`` is still preferred when writing RTL models.

-------------------------------------------------------------------------------
Prefer "random.randrange()" over "random.randint()"
-------------------------------------------------------------------------------

When creating randomized testing harnesses, the ``random`` package comes in
handy for generating inputs in a specific value range. The ``random.randint()``
method is usually used for this purpose, however, it's semantics differ from
those of ``range()`` which often leads to confusion (``range(start, stop)`` has
an inclusive start and *exclusive* stop, whereas ``randint(start, stop)`` has
an inclusive start **and** stop).

To address this issue, the ``random`` package now has added a ``randrange()``
method whose behavior matches that of ``range()``. This has the additional
benefit of better matching the computed bounds of 2's complement numbers::

  def okay_set_inputs( model ):
    for input in range( model.inputs ):
      input.value = random.randint( -(2**nbits), (2**nbits) - 1 )

  def better_set_inputs( model ):
    for input in range( model.inputs ):
      input.value = random.randrange( -(2**nbits), 2**nbits )

