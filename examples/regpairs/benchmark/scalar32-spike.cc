// SPDX-License-Identifier: Apache-2.0
// Scalar prototype: every operand names one independent RV32 register.
#include "extension.h"
#include "trap.h"
#include <cstdint>
class seal5_scalar32 : public extension_t {
public:
  const char *name() const override { return "seal5_scalar32"; }
  static reg_t execute(processor_t *p, insn_t insn, reg_t pc) {
    if (p->get_xlen() != 32)
      throw trap_illegal_instruction(insn.bits());
    uint32_t a = p->get_state()->XPR[insn.rs1()];
    uint32_t b = p->get_state()->XPR[insn.rs2()];
    uint32_t result;
    if (((insn.bits() >> 12) & 7) == 0) {
      unsigned count = (insn.bits() >> 25) & 31;
      result = uint32_t(((uint64_t(b) << 32) | a) >> count);
    } else {
      unsigned third = (insn.bits() >> 27) & 31;
      result = a + b + uint32_t(p->get_state()->XPR[third]);
    }
    p->get_state()->XPR.write(insn.rd(), reg_t(int64_t(int32_t(result))));
    return reg_t(int64_t(int32_t(uint32_t(pc + 4))));
  }
  std::vector<insn_desc_t> get_instructions(const processor_t &) override {
    return {{0x0b, 0xc000707f, execute, execute, execute, execute, execute,
             execute, execute, execute},
            {0x100b, 0x0600707f, execute, execute, execute, execute, execute,
             execute, execute, execute}};
  }
  std::vector<disasm_insn_t *>
  get_disasms(const processor_t * = nullptr) override {
    return {};
  }
};
REGISTER_EXTENSION(seal5_scalar32, []() { return new seal5_scalar32; })
