// SPDX-License-Identifier: Apache-2.0
// Independent functional model. Build against the Spike executable's headers.
#include "extension.h"
#include "trap.h"
#include <cstdint>

class seal5_regpairs : public extension_t {
public:
  const char *name() const override { return "seal5_regpairs"; }
  static reg_t execute(processor_t *p, insn_t insn, reg_t pc) {
    if (p->get_xlen() != 32 || ((insn.rd() | insn.rs1() | insn.rs2()) & 1))
      throw trap_illegal_instruction(insn.bits());
    auto read = [&](unsigned r) -> uint64_t {
      if (!r) return 0; // x0 pair never reads x1.
      return uint32_t(p->get_state()->XPR[r]) |
             (uint64_t(uint32_t(p->get_state()->XPR[r + 1])) << 32);
    };
    // Snapshot both sources before either destination word is written.
    uint64_t a = read(insn.rs1()), b = read(insn.rs2());
    uint64_t result;
    switch ((insn.bits() >> 12) & 7) {
    case 0: result = a + b; break;
    case 1: result = uint32_t(a + b) |
                    (uint64_t(uint32_t((a >> 32) + (b >> 32))) << 32); break;
    case 2: result = a - b; break;
    case 3: result = uint32_t(uint32_t(a) - uint32_t(b)) |
                    (uint64_t(uint32_t(uint32_t(a >> 32) - uint32_t(b >> 32))) << 32); break;
    case 4: result = uint32_t(uint32_t(a) * uint32_t(b)) |
                    (uint64_t(uint32_t(uint32_t(a >> 32) * uint32_t(b >> 32))) << 32); break;
    default: throw trap_illegal_instruction(insn.bits());
    }
    if (insn.rd()) {
      p->get_state()->XPR.write(insn.rd(), reg_t(int64_t(int32_t(result))));
      p->get_state()->XPR.write(insn.rd() + 1,
                                reg_t(int64_t(int32_t(result >> 32))));
    }
    return reg_t(int64_t(int32_t(uint32_t(pc + 4))));
  }
  std::vector<insn_desc_t> get_instructions(const processor_t &) override {
    std::vector<insn_desc_t> result;
    for (unsigned match : {0x0bu, 0x100bu, 0x200bu, 0x300bu, 0x400bu})
      result.push_back({match, 0xfe00707f, execute, execute, execute, execute,
                        execute, execute, execute, execute});
    return result;
  }
  std::vector<disasm_insn_t *> get_disasms(const processor_t * = nullptr) override {
    return {};
  }
};
REGISTER_EXTENSION(seal5_regpairs, []() { return new seal5_regpairs; })
