# Seal5

TODO: Summary

## Prerequisites

### Ubuntu Packages

TODO: cmake, ninja, make,...

### Python Requirements

First, setup a virtual environment with Python v3.8 or newer.

Install all required python packages using the follow8n* command:

`pip install -r requirements.txt`.

TODO: dev requirements

### Installation

#### From PyPI

TODO: Publish after open-source release.

#### Local Development Version

First prepare your shell by executing `export PYTHONPATH=$(pwd):$PYTHONPATH` inside the seal5 repository. Then you should be able to use Seal5 without needing to reinstall it.

Alternatively you should be able to use `pip install -e .`.

## Usage

### Python API

The flow can be sketched as follows (see Example below for functional code!):

```python
# Create flow
seal5_flow = Seal5Flow(...)
# Initialize LLVM repo and .seal5 directories
seal5_flow.initialize(...)
# Optional: remove artifacts from previous builds
seal5_flow.reset(...)
# Install Seal5 dependencies (CDSL2LLVM/PatternGen)
seal5_flow.setup(...)
# Load CoreDSL2+CFG files (Git config, filters,...)
seal5_flow.load(...)
# Transform Seal5 model (Extract side effects, operands,...)
seal5_flow.transform(...)
# Generate patches based on Seal5 model (ISel patterns, RISC-V features,...)
seal5_flow.generate(...)
# Apply generated (and manual) patches to LLVM codebase
seal5_flow.patch(...)
# Build patches LLVM (This will take a while)
seal5_flow.build(...)
# Run LLVM+Seal5 tests to verify functionality
seal5_flow.test(...)
# Combine patches and install LLVM
seal5_flow.deploy(...)
# Archive final llvm (optionally inclusing logs, reports,...)
seal5_flow.export(...)
# Optional: Cleanup all artifacts
seal5_flow.cleanup(...)
```

### Command-Line Interface

TODO: Not yet implemented...

## Examples

See ['examples/demo.py'](examples/demo.py) for example of end-to-end flow!

## Documentation

TODO: Sphinx Documentation

## Limitations

See [here](./LIMITATIONS.md).

## Contributions

Seal5 issue tracker: https://github.com/tum-ei-eda/seal5/issues

CoreDSL2LLVM/PatternGen issue tracker: https://github.com/mathis-s/CoreDSL2LLVM/issues

## References
