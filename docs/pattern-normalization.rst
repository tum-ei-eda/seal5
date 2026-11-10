Optional pattern normalizations
===============================

The following transform passes are disabled by default. Enable them individually
using pass overrides in the Seal5 configuration::

    passes:
      overrides:
        explicit_memory_names:
          enabled: true
        explicit_register_names:
          enabled: true
        normalize_subscripts:
          enabled: true
        detect_branches:
          enabled: true

They run after the final type inference and before CoreDSL output, including the
split output consumed by pattern-gen. To verify the transforms independently of
an LLVM build, run::

    python -m seal5.transform.pattern_normalization input.seal5model \
        --explicit-memory-names --explicit-register-names \
        --normalize-subscripts --detect-branches -o output.seal5model

Memory ranges have inclusive bounds and byte-sized elements. Thus
``MEM[a+1:a]`` becomes ``MEM16[a]``, and ``MEM[a+3:a]`` becomes
``MEM32[a]``. A single-byte access becomes ``MEM8[a]``. The XLEN-sized
variant uses ``MEMX``. Ascending memory ranges have the opposite byte order
and are retained. Unsupported widths are retained as well. Existing explicit
names are left unchanged.

On RV64, ``X[index][31:0]`` becomes ``XW[index]``. Other slices and RV32
register accesses are retained.

Scalar bit ranges select the same bits in either direction. Both
``value[base+4:base]`` and ``value[base:base+4]`` become
``value[base +: 5]``. This applies to register values and local scalar values,
including assignment targets. Unlike scalar bit ranges, address-space ranges
have direction-sensitive concatenation semantics. They are not normalized by
this pass. See the `CoreDSL range specification
<https://github.com/Minres/CoreDSL/wiki/Expressions#range-operator>`_.

The LLVM 23 reference parser adds the width when calculating the lower bound
of ``-:``. The transform therefore emits only ``+:`` and does not depend on
that implementation of ``-:``.

Branch detection currently recognizes a single conditional PC-relative update,
``if (condition) PC = PC + immediate;``. It retains the condition in
``branch(condition)`` and marks the displacement operand ``is_branch_offs``.
The model also retains the original displacement expression. The canonical
nested alignment check (raise on misalignment, otherwise update PC) is lowered
while retaining both its guard and trap. Unrecognized additional effects and
else blocks prevent the rewrite. Existing branch calls are retained. This transform alone does not enable branch pattern
generation on LLVM 23 or remove ``skip_pattern_gen`` annotations.

Manual explicit names
---------------------

Seal5's frontend accepts ``MEM8``, ``MEM16``, ``MEM32``, ``MEM64``, and
``MEMX`` as typed views of a declared ``MEM`` memory. On RV64, ``XW`` is
a 32-bit view of the declared ``X`` register bank. These views retain the
architectural attributes used for memory and register operand detection.
Normal source declarations and local variables take precedence over the
builtins. Unknown identifiers still cause frontend errors.

``branch(condition);`` is accepted without a function declaration. It remains
an explicit branch call through the optional transforms. The frontend is used
automatically by Seal5's load operation and can also be invoked directly::

    python -m seal5.frontends.coredsl input.core_desc -o model_directory

Remaining integration work
--------------------------

General address-space subscript normalization remains to be implemented with
byte-order preservation. The retained alignment-trap guards may require
additional pattern-gen support; this work currently verifies the transforms
independently of LLVM pattern generation.
