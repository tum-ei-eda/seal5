// SPDX-License-Identifier: Apache-2.0
// Functional model of the four demo instructions, plus measurement markers.
// Build against the headers of the Spike executable being used (unstable ABI).
#include "extension.h"
#include "trap.h"
#include <array>
#include <cstdint>
#include <cstdio>

class seal5_packed : public extension_t {
  std::array<uint64_t, 4> counts{};

public:
  const char *name() const override { return "seal5_packed"; }
  void reset(processor_t &) override { counts.fill(0); }
  static reg_t execute(processor_t *p, insn_t insn, reg_t pc) {
    if (p->get_xlen() != 32)
      throw trap_illegal_instruction(insn.bits());
    auto *ext = static_cast<seal5_packed *>(p->get_extension("seal5_packed"));
    unsigned kind = unsigned(insn.bits() >> 12) & 7;
    if (kind == 7) {
      if ((insn.bits() >> 25) == 0) {
        ext->counts.fill(0);
      } else {
        std::fprintf(
            stderr,
            "SEAL5_MEASURE {\"instructions\":%u,\"spike_model_cycles\":%u,"
            "\"pack.add.4x8\":%llu,\"pack.add.2x16\":%llu,"
            "\"pack.sub.4x8\":%llu,\"pack.sub.2x16\":%llu}\n",
            uint32_t(p->get_state()->XPR[insn.rs1()]),
            uint32_t(p->get_state()->XPR[insn.rs2()]),
            (unsigned long long)ext->counts[0],
            (unsigned long long)ext->counts[1],
            (unsigned long long)ext->counts[2],
            (unsigned long long)ext->counts[3]);
      }
    } else {
      unsigned bits = kind == 0 ? 8 : 16;
      bool subtract = ((insn.bits() >> 25) & 1) != 0;
      uint32_t a = p->get_state()->XPR[insn.rs1()];
      uint32_t b = p->get_state()->XPR[insn.rs2()];
      uint32_t mask = (1u << bits) - 1;
      uint32_t result = 0;
      for (unsigned shift = 0; shift < 32; shift += bits) {
        uint32_t x = (a >> shift) & mask, y = (b >> shift) & mask;
        result |= ((subtract ? x - y : x + y) & mask) << shift;
      }
      p->get_state()->XPR.write(insn.rd(), reg_t(int64_t(int32_t(result))));
      ++ext->counts[2 * subtract + kind];
    }
    return reg_t(int64_t(int32_t(uint32_t(pc + 4))));
  }
  std::vector<insn_desc_t> get_instructions(const processor_t &) override {
    std::vector<insn_desc_t> result;
    for (unsigned match :
         {0x2bu, 0x102bu, 0x0200002bu, 0x0200102bu, 0x702bu, 0x0200702bu})
      result.push_back({match, 0xfe00707f, execute, execute, execute, execute,
                        execute, execute, execute, execute});
    return result;
  }
  std::vector<disasm_insn_t *>
  get_disasms(const processor_t * = nullptr) override {
    return {};
  }
};
REGISTER_EXTENSION(seal5_packed, []() { return new seal5_packed; })
