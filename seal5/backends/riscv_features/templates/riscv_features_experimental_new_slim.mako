def Feature${predicate} : RISCVExperimentalExtension<"${arch}", ${major}, ${minor}, "${description}">;
def Has${predicate} : Predicate<"Subtarget->has${predicate}()">, AssemblerPredicate<(any_of Feature${predicate}), "'${feature}' (${description})">;
