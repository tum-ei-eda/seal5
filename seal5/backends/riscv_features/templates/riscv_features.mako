def Feature${predicate} : SubtargetFeature<"${arch}", "Has${predicate}", "true", "'${feature}' (${description})">;
def Has${predicate} : Predicate<"Subtarget->has${predicate}()">, AssemblerPredicate<(any_of Feature${predicate}), "'${feature}' (${description})">;
