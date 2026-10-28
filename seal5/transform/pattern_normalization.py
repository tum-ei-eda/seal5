# SPDX-License-Identifier: Apache-2.0
"""Run optional pattern-gen normalizations on a saved Seal5 model.

Example::

    python -m seal5.transform.pattern_normalization input.seal5model \
        --explicit-memory-names --explicit-register-names \
        --normalize-subscripts --detect-branches -o output.seal5model
"""

import argparse

from seal5.model import Seal5InstrAttribute, Seal5OperandAttribute
from seal5.model_utils import dump_model, load_model
from seal5.transform.detect_branches import detect_branch
from seal5.transform.explicit_names import ExplicitNames
from seal5.transform.normalize_subscripts import NormalizeSubscripts


def transform_model(model, *, memory=False, registers=False, subscripts=False, branches=False):
    """Apply requested transforms and return per-transform rewrite counts."""
    counts = {"memory": 0, "registers": 0, "subscripts": 0, "branches": 0}
    for set_def in model.sets.values():
        visitors = []
        if memory:
            visitors.append(("memory", ExplicitNames(set_def.xlen, memory=True)))
        if registers:
            visitors.append(("registers", ExplicitNames(set_def.xlen, registers=True)))
        if subscripts:
            visitors.append(("subscripts", NormalizeSubscripts(set_def.xlen, memory=memory)))
        for instr in set_def.instructions.values():
            for _, visitor in visitors:
                instr.operation = visitor.generate(instr.operation)
            if branches:
                operation, offset_name = detect_branch(instr.operation, instr.operands)
                if offset_name is not None:
                    instr.operation = operation
                    instr.operands[offset_name].attributes[Seal5OperandAttribute.IS_BRANCH_OFFS] = []
                    instr.attributes[Seal5InstrAttribute.IS_BRANCH] = []
                    counts["branches"] += 1
        for name, visitor in visitors:
            counts[name] += visitor.changed
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--explicit-memory-names", action="store_true")
    parser.add_argument("--explicit-register-names", action="store_true")
    parser.add_argument("--normalize-subscripts", action="store_true")
    parser.add_argument("--detect-branches", action="store_true")
    args = parser.parse_args(argv)
    model = load_model(args.model)
    counts = transform_model(
        model,
        memory=args.explicit_memory_names,
        registers=args.explicit_register_names,
        subscripts=args.normalize_subscripts,
        branches=args.detect_branches,
    )
    dump_model(model, args.output)
    print(counts)


if __name__ == "__main__":
    main()
