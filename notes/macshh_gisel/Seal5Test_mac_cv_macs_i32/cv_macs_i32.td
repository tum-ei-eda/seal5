let Predicates = [HasVendorSeal5Testmaccvmacsi32] in {
let hasSideEffects = 0, mayLoad = 0, mayStore = 0, isCodeGenOnly = 1, Constraints = "$rd = $rd_wb" in def cv_macs_i32_ : RVInst_cv_macs_i32<(outs GPR:$rd_wb), (ins GPR:$rd, GPR:$rs1, GPR:$rs2)>;

def : Pat<
	(i32 (add (mul GPR:$rs2, GPR:$rs1), GPR:$rd)),
	(cv_macs_i32_ GPR:$rd, GPR:$rs1, GPR:$rs2)>;

}
