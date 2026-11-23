# Immediate operand-type collection follow-up

Investigated the archived `seal5-diss-exp` extraction attempt
`20261123T162843Z-65e500a2ff4b4cc89526ee83ced9f80a` without modifying its cache
or results. No compiler rebuild was needed for this fix.

The operand-type collector reproduced all 20 reported SIMD transformation
failures using the cached `XCoreVSimd.seal5model`. With exception diagnostics
enabled, every failure was `AssertionError: sign/zero extension not allowed here`
in the immediate TypeConv visitor.

A widening cast describes an expression's value, rather than changing the
encoded immediate's width or signedness. The collector now preserves the
operand's encoding type and keeps the explicit cast in the behavior. In
particular, converting unsigned<6> to signed<16> must not reclassify the encoded
immediate as signed<6>. Same-width cast inference remains supported; truncating
casts still fail explicitly.

After the fix, all 220 SIMD instructions pass this collector without
`--skip-failing`. Comparing operand datatype, width and lane count against the
cached model finds no changes. This explains why some affected instructions
could previously extract successfully despite the warning.

Regression tests cover widening signed and unsigned immediates to signed and
unsigned 8/16/32/64-bit expressions, same-width signed casts, rejected truncation,
and diagnostic/fail-fast behavior. Local evidence is under
`/tmp/seal5-simd-easy-fixes`.

This resolves the operand-type warnings only. It does not establish a reduction
in the separate 101 extraction failures or validate additional generated code.
