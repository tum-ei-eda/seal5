def Feature${predicate} : RISCVExperimentalExtension<"${arch}", ${major}, ${minor}, "'${feature}' (${description})", ${implies}>;
def Has${predicate} : Predicate<"Subtarget->has${predicate}()">, AssemblerPredicate<(any_of Feature${predicate}), "'${feature}' (${description})">;
