let Predicates = [HasVendorSeal5TestmaccvmachhNs] in {
let hasSideEffects = 0, mayLoad = 0, mayStore = 0, isCodeGenOnly = 1, Constraints = "$rd = $rd_wb" in def cv_machhNs_ : RVInst_cv_machhNs<(outs GPR:$rd_wb), (ins GPR:$rd, GPR:$rs1, GPR:$rs2, uimm5:$Is3)>;

def : Pat<
	(i32 (i32 (sra (add (mul (i32 (sra (i32 (shl (i32 (srl GPR:$rs2, (i32 16))), (i32 16))), (i32 16))), (i32 (sra (i32 (shl (i32 (srl GPR:$rs1, (i32 16))), (i32 16))), (i32 16)))), GPR:$rd), (and (i32 uimm5:$Is3), (i32 31))))),
	(cv_machhNs_ GPR:$rd, GPR:$rs1, GPR:$rs2, uimm5:$Is3)>;

}
