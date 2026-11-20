// SPDX-License-Identifier: Apache-2.0
// Count executed instructions independently of ETISS's cycle-derived instret.
#include "etiss/CPUCore.h"
#include "etiss/ETISS.h"
#include "etiss/Instruction.h"
#include "etiss/Plugin.h"
#include "etiss/SimpleMemSystem.h"
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>

class Counter : public etiss::TranslationPlugin {
public:
  mutable uint64_t active = 0, total = 0, starts = 0, ends = 0;
  mutable uint64_t cycle_start = 0, cycle_end = 0;
  mutable uint64_t traced = 0;
  mutable std::map<std::string, uint64_t> counts;
  uint64_t start, end;
  explicit Counter(uint64_t start, uint64_t end) : start(start), end(end) {}
  std::string _getPluginName() const override { return "Seal5Counter"; }
  static std::string slot(const uint64_t *p) {
    return "(*(uint64_t *)(uintptr_t)" +
           std::to_string(reinterpret_cast<uintptr_t>(p)) + "ULL)";
  }
  void initCodeBlock(etiss::CodeBlock &block) const override {
    if (etiss::cfg().get<bool>("seal5.trace", false))
      block.fileglobalCode().insert("extern int printf(const char *, ...); extern int fflush(void *);");
  }
  void finalizeInstrSet(etiss::instr::ModedInstructionSet &mis) const override {
    mis.foreach([this](etiss::instr::VariableInstructionSet &vis) {
      vis.foreach([this](etiss::instr::InstructionSet &set) {
        set.foreach([this](etiss::instr::Instruction &instr) {
          instr.addCallback(
              [this, &instr](etiss::instr::BitArray &ba, etiss::CodeSet &cs,
                             etiss::instr::InstructionContext &ic) {
                std::ostringstream code;
                if (etiss::cfg().get<bool>("seal5.trace", false))
                  code << "if (" << slot(&traced) << " < 300) { ++" << slot(&traced)
                       << "; printf(\"TRACE " << ic.current_address_
                       << " a0=%x a1=%x a2=%x a5=%x sp=%x\\n\","
                       << "*((RV32IMACFDXCoreV*)cpu)->X[10], *((RV32IMACFDXCoreV*)cpu)->X[11],"
                       << "*((RV32IMACFDXCoreV*)cpu)->X[12], *((RV32IMACFDXCoreV*)cpu)->X[15],"
                       << "*((RV32IMACFDXCoreV*)cpu)->X[2]); fflush(0); }\n";
                if (ic.current_address_ == start)
                  code << slot(&active) << " = 1; ++" << slot(&starts) << ";\n"
                       << slot(&cycle_start) << " = cpu->cpuTime_ps / cpu->cpuCycleTime_ps;\n";
                if (ic.current_address_ == end)
                  code << slot(&active) << " = 0; ++" << slot(&ends) << ";\n"
                       << slot(&cycle_end) << " = cpu->cpuTime_ps / cpu->cpuCycleTime_ps;\n";
                std::string name;
                std::istringstream(instr.printASM(ba)) >> name;
                code << "if (" << slot(&active) << ") { ++" << slot(&total)
                     << "; ++" << slot(&counts[name]) << "; }\n";
                cs.append(etiss::CodePart::PREINITIALDEBUGRETURNING).code() = code.str();
                return true;
              }, 0);
        });
      });
    });
  }
};

int main(int argc, const char **argv) {
  etiss::Initializer initializer(argc, argv);
  auto memory = std::make_shared<etiss::SimpleMemSystem>();
  memory->init_memory();
  auto cpu = etiss::CPUCore::create("RV32IMACFDXCoreV", "core0");
  if (!cpu)
    return 2;
  cpu->setTimer(false);
  uint64_t address = memory->get_startaddr();
  cpu->reset(&address);
  initializer.loadIniJIT(cpu);
  auto counter = std::make_shared<Counter>(
      etiss::cfg().get<uint64_t>("seal5.roi_start", 0),
      etiss::cfg().get<uint64_t>("seal5.roi_end", 0));
  cpu->addPlugin(counter);
  auto status = cpu->execute(*memory);
  std::cout << "SEAL5_COUNTS {\"instructions\":" << counter->total
            << ",\"model_cycles\":" << counter->cycle_end - counter->cycle_start
            << ",\"starts\":" << counter->starts << ",\"ends\":" << counter->ends
            << ",\"active\":" << counter->active << ",\"mnemonics\":{";
  bool first = true;
  for (const auto &entry : counter->counts) {
    if (!entry.second)
      continue;
    if (!first)
      std::cout << ',';
    first = false;
    std::cout << '"' << entry.first << "\":" << entry.second;
  }
  std::cout << "}}\n";
  return status == etiss::RETURNCODE::CPUFINISHED ? 0 : 1;
}
