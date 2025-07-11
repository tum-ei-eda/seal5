## Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
## Copyright (c) 2025 DLR-SE Department of System Evolution and Operation
#
# Generated on ${start_time}.
#
# This file contains the Info for generating invalid tests for the ${set_name}
# core architecture.


# RUN: ${"not llvm-mc -triple=riscv%s --mattr=+%s %%s 2>&1 \\" % (xlen, arch)}
# RUN:        | FileCheck %s --check-prefixes=CHECK-ERROR

% for loop_cnt, op_str in enumerate((matrix)):
    % if (loop_cnt < (len(matrix)/2)):
${mnemonic} ${', '.join(op_str[0:len(op_str)-1])} # CHECK-ERROR: invalid operands for instruction
    % elif ((loop_cnt == ((len(matrix))/2)) ):
${mnemonic} ${', '.join(op_str[0:len(op_str)-2])} # CHECK-ERROR: too few operands for instruction
${mnemonic} ${', '.join(op_str[1:len(op_str)-1])} # CHECK-ERROR: too few operands for instruction
    % elif (loop_cnt == (len(matrix)/2)+1):
${mnemonic} ${', '.join(op_str[0:len(op_str)])} # CHECK-ERROR: too many operands for instruction
    %endif
% endfor
