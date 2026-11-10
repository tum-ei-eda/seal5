# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Export an M2-ISA-R model and its behavior as a Graphviz diagram."""

import argparse
import logging
from collections import defaultdict
from pathlib import Path

from anytree import Node, RenderTree
from anytree.exporter import UniqueDotExporter
from m2isar.metamodel import arch

from seal5.model_utils import load_model

from .treegen import TreeGenVisitor
from .utils import TextTreeGenContext

logger = logging.getLogger("backends.dot")


def sort_instruction(entry):
    """Sort instructions by encoding restrictiveness."""
    (code, mask), _ = entry
    return bin(mask).count("1"), code


def describe_type(value):
    """Return the current M2-ISA-R type representation for a model value."""
    return str(value.ty)


def _attribute_name(attribute):
    return getattr(attribute, "name", str(attribute))


def _dot_escape(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def _node_attributes(node):
    label = node.name
    value = getattr(node, "value", None)
    if value is not None:
        label = f"{label}\n{value}"
    return f'shape=box,label="{_dot_escape(label)}"'


def _add_behavior(parent, attributes, visitor, include_operations):
    attributes_node = Node("Attributes", parent=parent)
    for attribute, operations in attributes.items():
        attribute_node = Node(_attribute_name(attribute), parent=attributes_node)
        if include_operations:
            for operation in operations:
                visitor.generate(operation, TextTreeGenContext(parent=attribute_node))


def build_tree(model_obj, include_operations=False):
    """Build the hierarchy and, optionally, behavior tree for a model."""
    root = Node("SEAL5 Model")
    sets_node = Node("Sets", parent=root)
    visitor = TreeGenVisitor()

    for set_name, set_def in sorted(model_obj.sets.items()):
        set_node = Node(set_name, parent=sets_node)

        constants_node = Node("Constants", parent=set_node)
        for const_name, const_def in sorted(set_def.constants.items()):
            Node(const_name, parent=constants_node, value=str(const_def.value))

        memories_node = Node("Memories", parent=set_node)
        for mem_name, mem_def in sorted(set_def.memories.items()):
            Node(mem_name, parent=memories_node, value=describe_type(mem_def))

        aliases_node = Node("Memory Aliases", parent=set_node)
        for mem_name, mem_def in sorted(set_def.memory_aliases.items()):
            Node(
                f"{mem_name} ({mem_def.parent.name})",
                parent=aliases_node,
                value=describe_type(mem_def),
            )

        functions_node = Node("Functions", parent=set_node)
        for fn_name, fn_def in set_def.functions.items():
            fn_node = Node(fn_name, parent=functions_node, value="extern" if fn_def.extern else None)
            Node("Return", parent=fn_node, value=str(fn_def.ty))
            Node("Throws", parent=fn_node, value=str(fn_def.throws))
            _add_behavior(fn_node, fn_def.attributes, visitor, include_operations)

            params_node = Node("Parameters", parent=fn_node)
            for param_name, param_def in fn_def.args.items():
                Node(param_name, parent=params_node, value=describe_type(param_def))

            if include_operations:
                visitor.generate(fn_def.operation, TextTreeGenContext(parent=fn_node))

        instructions_by_size = defaultdict(dict)
        for key, instruction in set_def.instructions.items():
            instructions_by_size[instruction.size][key] = instruction

        instructions_node = Node("Instructions", parent=set_node)
        for size, instructions in sorted(instructions_by_size.items()):
            size_node = Node(f"Width {size}", parent=instructions_node)
            ordered_instructions = sorted(instructions.items(), key=sort_instruction, reverse=True)

            for (code, mask), instruction in ordered_instructions:
                opcode = f"{code:0{int(instruction.size / 4)}x}:{mask:0{int(instruction.size / 4)}x}"
                instruction_node = Node(
                    f"{instruction.ext_name} : {instruction.name}",
                    parent=size_node,
                    value=opcode,
                )

                encoding = []
                for field in instruction.encoding:
                    if isinstance(field, arch.BitVal):
                        encoding.append(f"{field.value:0{field.length}b}")
                    elif isinstance(field, arch.BitField):
                        encoding.append(f"{field.name}[{field.range.upper}:{field.range.lower}]")
                Node("Encoding", parent=instruction_node, value=" ".join(encoding))
                Node("Assembly", parent=instruction_node, value=str(instruction.assembly))
                Node("Throws", parent=instruction_node, value=str(instruction.throws))
                _add_behavior(instruction_node, instruction.attributes, visitor, include_operations)

                if include_operations:
                    visitor.generate(instruction.operation, TextTreeGenContext(parent=instruction_node))

    return root


def _print_tree(root):
    print("============================")
    for prefix, _, node in RenderTree(root):
        value = getattr(node, "value", None)
        suffix = f" [{value}]" if value is not None else ""
        print(f"{prefix}{node.name}{suffix}")
    print("============================")


def export_tree(root, output_path):
    """Write a tree as DOT source or a Graphviz-rendered image."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    exporter = UniqueDotExporter(root, nodeattrfunc=_node_attributes, maxlevel=100)
    if output_path.suffix.lower() == ".dot":
        exporter.to_dotfile(output_path)
    else:
        exporter.to_picture(str(output_path))
    return output_path


def main():
    """Load a model and export its visualization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("top_level", type=Path, help="A .seal5model or .m2isarmodel file.")
    parser.add_argument("--text", "-t", action="store_true", help="Also print the model tree.")
    parser.add_argument("--operation", "-o", action="store_true", help="Include instruction and function behavior.")
    parser.add_argument("--output", type=Path, help="Output file (.dot or a Graphviz-supported image format).")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--compat", action="store_true", help="Load an M2-ISA-R compatibility model.")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper()))
    model_path = args.top_level.resolve()

    if model_path.suffix == ".core_desc":
        logger.warning(".core_desc input is deprecated; loading its generated compatibility model")
        model_path = model_path.parent / "gen_model" / f"{model_path.stem}.m2isarmodel"
        args.compat = True

    model = load_model(model_path, compat=args.compat)
    root = build_tree(model, include_operations=args.operation)

    if args.text:
        _print_tree(root)

    if args.output is None:
        output_dir = model_path.parent.parent if model_path.parent.name == "gen_model" else model_path.parent
        args.output = output_dir / "gen_output" / f"{model_path.stem}.dot"

    output_path = export_tree(root, args.output)
    logger.info("wrote model diagram to %s", output_path)


if __name__ == "__main__":
    main()
