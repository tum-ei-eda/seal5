// SPDX-License-Identifier: Apache-2.0
#include "extension.h"
#include "trap.h"
#include <cstdint>
class seal5_mont64 : public extension_t {
public:
  const char *name() const override { return "seal5_mont64"; }
  static reg_t execute(processor_t *p, insn_t i, reg_t pc) {
    unsigned kind = (i.bits() >> 12) & 7;
    if (p->get_xlen() != 32 || ((i.rs1() | i.rs2()) & 1) ||
        (kind == 0 && (i.rd() & 1)))
      throw trap_illegal_instruction(i.bits());
    auto read = [&](unsigned r) -> uint64_t {
      return r ? uint32_t(p->get_state()->XPR[r]) |
                     (uint64_t(uint32_t(p->get_state()->XPR[r + 1])) << 32)
               : 0;
    };
    uint64_t a = read(i.rs1()), b = read(i.rs2());
    uint64_t result = kind == 0 ? (a << 1) | (b >> 63) : a >= b;
    if (i.rd()) {
      p->get_state()->XPR.write(i.rd(), reg_t(int64_t(int32_t(result))));
      if (kind == 0)
        p->get_state()->XPR.write(i.rd() + 1,
                                  reg_t(int64_t(int32_t(result >> 32))));
    }
    return reg_t(int64_t(int32_t(uint32_t(pc + 4))));
  }
  std::vector<insn_desc_t> get_instructions(const processor_t &) override {
    return {{0x5b, 0xfe00707f, execute, execute, execute, execute, execute,
             execute, execute, execute},
            {0x105b, 0xfe00707f, execute, execute, execute, execute, execute,
             execute, execute, execute}};
  }
  std::vector<disasm_insn_t *>
  get_disasms(const processor_t * = nullptr) override {
    return {};
  }
};
REGISTER_EXTENSION(seal5_mont64, []() { return new seal5_mont64; })
