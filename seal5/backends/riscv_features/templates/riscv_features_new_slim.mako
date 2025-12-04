def Feature${predicate} : RISCVExtension<${major}, ${minor}, "${description}", ${implies}>;
def Has${predicate} : Predicate<"Subtarget->has${predicate}()">, AssemblerPredicate<(any_of Feature${predicate}), "'${feature}' (${description})">;
