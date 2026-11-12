GNU binutils and GDB backend
============================

Seal5 can generate a unified patch for GNU GAS, ld, objdump and GDB's shared
RISC-V disassembler. This lets the GNU tools assemble custom mnemonics, retain
custom ISA attributes when linking LLVM-produced objects, and display the same
mnemonics in objdump and GDB. No GCC or C library rebuild is needed.

Generate the patch
------------------

First run the normal Seal5 transform pipeline. The backend consumes its
``.seal5/models/*.seal5model`` files, after register and immediate operand
collection. Generate against the **unpatched source checkout you will build**;
source files are read but never modified by the generator::

    source venv310/bin/activate
    python -m seal5.backends.riscv_gnu.writer \
      /tmp/seal5_llvm_demo_llvm23/.seal5/models/Example.seal5model \
      /tmp/seal5_llvm_demo_llvm23/.seal5/models/XCoreVNand.seal5model \
      --source /path/to/binutils-gdb \
      --output /tmp/seal5-gnu.patch

Pass all the models together to produce one patch. A sibling
``/tmp/seal5-gnu.json`` lists the generated instructions and extension names.
The patch is relative to the binutils/GDB source root, not the Seal5 root.
Already-patched checkouts and unfamiliar source layouts are rejected.

To enable the backend during ``seal5 generate``, set
``SEAL5_GNU_SOURCE=/path/to/binutils-gdb``. Alternatively add a configuration::

    passes:
      overrides:
        riscv_gnu:
          source: /path/to/binutils-gdb

The flow writes ``.seal5/patches/binutils-gdb/seal5.patch`` and ``seal5.json``.
Generation is disabled when no source is configured. GNU patches are applied
separately from Seal5's LLVM patch stages.

Using riscv-gnu-toolchain
-------------------------

If using a riscv-gnu-toolchain checkout, initialize its ``binutils`` submodule
and use that directory as ``--source``. Generate and apply a separate patch
against its ``gdb`` submodule if GDB comes from a different checkout/revision.
Each contains the shared binutils/GDB source tree; a patch generated for one
revision should not be assumed to apply to the other::

    cd /path/to/riscv-gnu-toolchain
    git submodule update --init --depth 1 binutils
    # Optional, for the debugger:
    git submodule update --init --depth 1 gdb

Apply the generated patch from the source root::

    cd /path/to/binutils-gdb
    git apply --check /tmp/seal5-gnu.patch
    git apply /tmp/seal5-gnu.patch

To regenerate, first reverse the old patch with
``git apply -R /tmp/seal5-gnu.patch`` or use a fresh checkout. Save the old
patch until it has been reversed.

Fast build: assembler, linker and objdump
-----------------------------------------

Use a separate build directory. A native C/C++ compiler, make, flex, bison,
texinfo and the normal binutils development dependencies are needed. On Debian
or Ubuntu, ``build-essential flex bison texinfo libgmp-dev libmpfr-dev`` cover
the core prerequisites. The following builds just the required cross tools,
without GCC, newlib, Linux, or a target sysroot::

    mkdir -p /tmp/seal5-gnu-build
    cd /tmp/seal5-gnu-build
    /path/to/binutils-gdb/configure \
      --target=riscv64-unknown-elf \
      --prefix="$HOME/.local/seal5-gnu" \
      --disable-werror --disable-nls --disable-sim --disable-gprofng \
      --without-debuginfod --without-python --without-guile
    make -j8 all-gas all-binutils all-ld

These tools support both RV32 and RV64 ELF. Select RV32 at assembly/link time,
not by rebuilding. Reduce ``-j8`` if memory is limited. Named make targets avoid
the much larger top-level riscv-gnu-toolchain build. The tools can be used
directly from the build tree::

    gas/as-new --version
    ld/ld-new --version
    binutils/objdump --version

Optionally install just these components::

    make install-gas install-binutils install-ld

Installed names have the ``riscv64-unknown-elf-`` prefix, even when processing
RV32 code.

Optional GDB
------------

With a patched combined source tree and the configuration above::

    make -j8 all-gdb
    gdb/gdb --version
    # Optional:
    make install-gdb

GDB is a host program and needs a C++17-capable compiler. GNU GMP and MPFR
headers/libraries are also required. Python, Guile, debuginfod and the simulator
are disabled above to reduce build dependencies. GDB is optional for the fast
binutils build; its disassembler uses the same generated opcode support.

If the toolchain's GDB submodule differs from its binutils submodule, use a
second build directory configured against the separately patched GDB checkout,
then run ``make -j8 all-gdb`` there.

Smoke test with the Seal5 demo
------------------------------

After generating the patch from both demo models, create ``/tmp/custom.s``::

    .attribute arch, "rv32i2p1_xcorevnand1p0_xexample1p0"
    .text
    .global _start
    _start:
      cv.nand.bitwise a0, a1, a2
      xexample.subincacc a0, a1, a2
      xexample.slli_add_addi a0, a1, a2, -4, 31

Run from the GNU build directory::

    gas/as-new -march=rv32i_xcorevnand_xexample -o /tmp/custom.o /tmp/custom.s
    ld/ld-new -m elf32lriscv -e _start -Ttext=0x1000 \
      -o /tmp/custom.elf /tmp/custom.o
    binutils/objdump -d /tmp/custom.elf
    gdb/gdb -nx -batch /tmp/custom.elf \
      -ex 'disassemble /r _start,_start+12'

Both decoders should display all three custom mnemonics. The last instruction
uses nonstandard register positions, two immediate fields and a negative
immediate; its encoding is ``9f62d457``.

LLVM-generated objects work directly with these tools. For example::

    demo=/tmp/seal5_llvm_demo_llvm23/.seal5/tests/Output
    ld/ld-new -m elf32lriscv -r -o /tmp/custom-linked.o \
      "$demo/cv-nand-bitwise.test-inline-asm.c.tmp.o" \
      "$demo/xexample-subincacc.test-inline-asm.c.tmp.o"
    binutils/readelf -A /tmp/custom-linked.o
    binutils/objdump -d /tmp/custom-linked.o

``readelf`` should show both ``xcorevnand1p0`` and ``xexample1p0`` in the merged
architecture attribute. This verifies that the linker accepts and merges the
custom extensions, rather than just preserving unknown instruction bytes.

The same demo checks can be repeated automatically from the Seal5 repository::

    source venv310/bin/activate
    python scripts/test_riscv_gnu.py --build /tmp/seal5-gnu-build \
      --gdb /tmp/seal5-gnu-build/gdb/gdb \
      --llvm-demo /tmp/seal5_llvm_demo_llvm23

Omit ``--gdb`` or ``--llvm-demo`` when those optional checks are unavailable.
The script also checks instruction words, immediate range errors and rejection
of custom mnemonics when the required extension is disabled.

Scope and source compatibility
------------------------------

The backend emits fixed-bit opcode matches, arbitrary split operand fields,
GPR/FPR operands, compressed GPR indices, numeric or named CSR operands,
signed/unsigned constant immediates, and vendor extension
version registrations. It uses existing RISC-V ELF relocations and does not
add relocation types for custom symbolic immediate operands. Custom immediate
arguments to GAS must currently be assembly-time constants. Hardware execution
and GDB simulation of instruction semantics are outside opcode/disassembler
support.

The generator checks the expected upstream source anchors and adapts to old
and current libopcodes printing and GAS expression interfaces. An upstream
source-layout change may require a generator update; generation fails instead
of silently leaving out a component. Current upstream binutils/GDB commit
``17d606a601f4957f9591b2bfb3f39b57716e531d`` was used for the initial complete
GAS/ld/objdump/GDB build and demo smoke test.
