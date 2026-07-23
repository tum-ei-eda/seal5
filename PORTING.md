# How to Port Seal5 to new LLVM reseases

Check [COMPATIBILITY.md](COMPATIBILITY.md) for LLVM versions currently supported by Seal5.

The following guide should document how the process of supporting new LLVM versions in Seal5 is. The goal should always be to keep the support for previous LLVM versions unless impossible. Make sure to test compatibility with earlier versions after applying patches specific to a new LLVM version.

The migration from LLVM 20 to LLVM 21 will be used as an example workflow.

## Porting of Seal5

1. Setup Seal5 as usual (clone, install into venv,...)
2. Create a new branch, i.e. `git checkout -b llvm-21-support`
3. Choose one tag of the new LLVM release, i.e. `llvmorg-21.1.7`
4. Creaty dummy `insert_maskers_llvm21.patch` based on an older version:

```sh
cd seal5/resources/patches/llvm
cp insert_markers_llvm20.patch insert_markers_llvm21.patch
```

4. Run Demo Flow with new LLVM version (without PatternGen):

```sh
PREPATCHED=0 SKIP_PATTERNS=0 LLVM_REF=llvmorg-21.1.7 DEST=/tmp/seal5_demo_llvm21 python3 examples/demo.py
```

5. With 99% probability, git will fail applying the patch. Now you will have to manually insert all the patch fraqments in the file. Once finished, you can commit the changes and override the dummy patch with the new version:

```sh
cd /tmp/seal5_demo_llvm21
# manually apply patch
git add .
git commit -m 'insert markers'
git show > /patch/to/seal5/seal5/resources/patches/llvm/insert_markers_llvm21.patch
```

Finally you have to remove the commit header and some biolerplate (i.e. indexes) from the patch manually.

6. Invoke the Seal5 demo again as explained above.

7. In case of errors, you will need to add fixes for them within Seal5 (i.e. pick different patches based on the uses LLVM major version, see for example [here](https://github.com/tum-ei-eda/seal5/blob/main/seal5/backends/riscv_features/writer.py#L64)).

8. Repeat this process until Seal5 finishes successfully (ideally without failing unit tests)

9. Now you should be ready to port the PatternGen integration (see next section)

10. Once the PatternGen is ported to the new LLVM version (i.e. under the `llvm-21.1.7` branch) you will have to handle the new LLVM major version in [`seal5/dependencies.py`](seal5/dependencies.py), see `pick_coredsl2llvm_ref` function.

11. Now you should be able to remove the `SKIP_PATTERN=0` to try the full flow with pattern-generation enabled. Fix any bugs/errors which occour either in Seal5 or in CoreDSL2LLVM.

12. Update [COMPATIBILITY.md](COMPATIBILITY.md) file
13. Add new LLVM version to CI matrix in [`.github/workflows/demo_weekly.yml`](.github/workflows/demo_weekly.yml)
14. Optional: Change default LLVM version in [`.github/workflows/demo.yml`](.github/workflows/demo.yml) as well
15. Commit changed and added files and push changes to GitHub: `git push origin llvm-21-support`
16. Manually trigger [Weekly CI Workflow](https://github.com/tum-ei-eda/seal5/actions/workflows/demo_weekly.yml) with used branch (i.e. `llvm-21-support`) and new LLVM version
17. If a relevant demo fails to pass the CI with the new LLVM version, you might want to look into that demo as well.
18. Open PR to merge the changes into the `main` or `develop` branch


## Porting PatternGen


1. Clone CoreDSL2LLVM Repository:

```sh
git clone git@github.com:PhilippvK/CoreDSL2LLVM.git
cd CoreDSL2LLVM
```

2. Checkout the (stable) patterngen branch for the last supported LLVM version: `git checkout -b llvm-20.1.0`

3. Add Upstream Git Remote:

```sh
git remote add upstream git@github.com:llvm/llvm-project.git
git fetch upstream
git fetch upstream --tags
```

4. Create new branch: `git checkout -b llvm-21.1.7 llvmorg-21.1.7`

5. Cherry pick all pattern-gen specific commits to the new LLVM version:

```sh
git cherry-pick llvmorg-20.1.0...llvm-20.1.0
```

While doing this, you will have to incrementally resolve merge conflicts which show up. Lets hope that they are rather simple!

6. After the cherry-pick was successful, make sure to check if the compilation succeeds as expected by doing a standalone build (outside of Seal5)

It is likely that some interfaces change between LLVM releases. If this affects Patterngen files in `llvm/tools/pattern-gen` or `llvm/lib/CodeGen/GlobalIsel/Patterngen.` you will have to write some small patches.


7. After the build completes, you can use the provided CoreDSL examples for testing the new PatternGen:

```sh
export PATH=$(pwd)/build/bin:$PATH
llvm-lit -v core_descs
```

Failing tests will have to be investigated. Sometimes FileCheck lines have to be adapted for the new LLVM version (ideally without breaking tests for older releases)

8. Don't forget to commit all fixes push the changes to GitHub in the end!

9. Continue testing the Seal5 integration as explained in the previous section.
