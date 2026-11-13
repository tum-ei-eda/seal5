# SPDX-License-Identifier: Apache-2.0
"""Memory address expressions read registers even on an assignment's left side."""
import unittest

from m2isar.metamodel import arch, behav, type_info
from seal5.transform.detect_inouts.collect import VisitorContext
from seal5.transform.detect_inouts.visitor import DetectInoutsVisitor


class MemoryInoutsTests(unittest.TestCase):
    def test_variable_lane_insert_reads_old_destination(self):
        kind = type_info.TypeKind.UINT
        registers = arch.RegisterBank("X", 32, kind, 32, {})
        rd = behav.NamedReference(arch.BitFieldDescr("rd", 5, kind))
        rs = behav.NamedReference(arch.BitFieldDescr("rs", 5, kind))
        offset = behav.NamedReference(arch.BitFieldDescr("offset", 2, kind))
        upper = behav.BinaryOperation(offset, behav.Operator("+"), behav.Literal(7))
        target = behav.SliceOperation(behav.IndexedReference(registers, rd), upper, offset)
        source = behav.SliceOperation(behav.IndexedReference(registers, rs), behav.Literal(7), behav.Literal(0))
        context = VisitorContext()
        DetectInoutsVisitor().generate(behav.Assignment(target, source), context)
        self.assertEqual(context.reads, {"rd", "rs", "offset"})
        self.assertEqual(context.writes, {"rd"})

    def test_indexed_store_reads_address_and_data(self):
        kind = type_info.TypeKind.UINT
        registers = arch.RegisterBank("X", 32, kind, 32, {})
        memory = arch.Memory("MEMX", kind, 32, 2**32, {})

        def register(name):
            return behav.IndexedReference(registers, behav.NamedReference(arch.BitFieldDescr(name, 5, kind)))

        address = behav.BinaryOperation(register("base"), behav.Operator("+"), register("index"))
        store = behav.Assignment(behav.IndexedReference(memory, address), register("data"))
        context = VisitorContext()
        DetectInoutsVisitor().generate(store, context)
        self.assertEqual(context.reads, {"base", "index", "data"})
        self.assertEqual(context.writes, set())

    def test_load_retains_register_destination(self):
        kind = type_info.TypeKind.UINT
        registers = arch.RegisterBank("X", 32, kind, 32, {})
        memory = arch.Memory("MEMX", kind, 32, 2**32, {})
        destination = behav.IndexedReference(registers, behav.NamedReference(arch.BitFieldDescr("rd", 5, kind)))
        address = behav.IndexedReference(registers, behav.NamedReference(arch.BitFieldDescr("base", 5, kind)))
        context = VisitorContext()
        DetectInoutsVisitor().generate(behav.Assignment(destination, behav.IndexedReference(memory, address)), context)
        self.assertEqual(context.reads, {"base"})
        self.assertEqual(context.writes, {"rd"})
