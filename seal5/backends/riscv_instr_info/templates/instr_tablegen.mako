def ${name} : Instruction, Sched<${sched_str}> {
    // General
    let Namespace = "RISCV";
    let Size = ${xlen // 8};
    bits<32> SoftFail = 0;
    bits<${xlen}> Inst;

    // Operands
    % for operand in operands:
    bits<${operand.length}> ${operand.name};
    % endfor

    // Attributes
    % for key, value in attrs.items():
    let ${key} = ${value};
    % endfor

    // Encoding
    % for enc in fields:

        % if enc.length == 1:
            % if enc.extra is None:
    let Inst{${enc.start}} = ${enc.name};
            % else:
    let Inst{${enc.start}} = ${bin(enc.extra)};${"  // " + enc.name if enc.name else ""}
            % endif
        % else:
            % if enc.extra is None:
    let Inst{${enc.start+enc.length-1}-${enc.start}} = ${enc.name};
            % else:
    let Inst{${enc.start+enc.length-1}-${enc.start}} = ${f"0b{enc.extra:0{enc.length}b}"};${"  // " + enc.name if enc.name else ""}
            % endif
        % endif
    % endfor


    // Operands
    dag InOperandList = (ins ${ins_str});
    dag OutOperandList = (outs ${outs_str});

    // Assembly
    let AsmString = "${real_name}\t${asm_str}";

    % if len(constraints_str):
    // Constraints
    let Constraints = "${constraints_str}";
    % endif
}
