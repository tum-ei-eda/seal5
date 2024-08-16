# Seal5

> [!NOTE]
> Starting **July 11, 2024** we will be offering (monthly) Seal5 Development/User meetings.
>
> Next call: **Sep 12, 2024, 11:00**
>
> Click [here](https://github.com/tum-ei-eda/seal5/discussions/104) for details, if you are interested!

> [!NOTE]
> Seal5 was recently presented at the RISC-V Summit Europe 2024. Click [here](https://github.com/tum-ei-eda/seal5/discussions/107) to access the poster, slides & recording.

[![pypi package](https://badge.fury.io/py/seal5.svg)](https://pypi.org/project/seal5)
[![readthedocs](https://readthedocs.org/projects/seal5/badge/?version=latest)](https://seal5.readthedocs.io/en/latest/?version=latest)
[![GitHub license](https://img.shields.io/github/license/tum-ei-eda/seal5.svg)](https://github.com/tum-ei-eda/seal5/blob/main/LICENSE)

[![demo workflow](https://github.com/tum-ei-eda/seal5/actions/workflows/demo.yml/badge.svg)](https://github.com/tum-ei-eda/seal5/actions/workflows/demo.yml)

## Overview

The RISC-V instruction set architecture (ISA) is popular for its extensibility. However, a quick exploration of instruction candidates fails due to the lack of tools to auto-generate embedded software toolchain support. Seal5 work establishes a semi-automated flow to generate LLVM compiler support for custom instructions based on the CoreDSL2 ISA description language. Seal5 is capable of generating support for functionalities ranging from baseline assembler-level support, over builtin functions to compiler code generation patterns for scalar as well as vector instructions, while requiring no deeper compiler know-how.

Eliminating manual efforts for Retargeting is crutial for the automated exploration of custom RISC-V instructions as depicted in the following image. Seal5's code-generation support allows to make use of custom instructions without needing to make changes to the programs/benchmarks source code (i.e. adding inline-assembly calls).

![ISADSESeal5](https://github.com/tum-ei-eda/seal5/assets/7712605/f387f13f-fc26-4efb-b6e0-d0802ac08200)

## Prerequisites

To be able to run the examples, make sure to clone the Seal5 repo using the `--recursive` flag. Otherwise run the following command to fetch (and update) the referenced submodules.

```sh
git submodule update --init --recursive
```

### Ubuntu Packages

First, a set of APT packages needs to be installed:

```sh
sudo apt install python3-pip python3-venv cmake make ninja-build
```

### Python Requirements

First, setup a virtual environment with Python v3.8 or newer.

Install all required python packages using the following command:

`pip install -r requirements.txt`.

For development (linting, packaging,...) there are a few more dependencies which can be installed via:

`pip install -r requirements_dev.txt`.

### System Requirements

The initial cloning of the `llvm-project` repo will take a long time, hence a good internet connection is recommended. To run the demo, make sure to have at least 20GB (>40GB for debug builds) of disk space available in the destination (`/tmp/seal5_llvm_demo`) directory. The target directory can be changed as follows: `DEST=$HOME/seal5_demo`.

### Installation

**Warning:** It is highly recommended to install `seal5` into a new virtual environment. Follow these steps to initialize and enter a venv in your seal5 repo directory:

```sh
# alternative: python3 -m venv venv
virtualenv -p python3.8 venv
source venv/bin/activate
```

#### From PyPI

```
pip install seal5
```

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
# Archive final LLVM (optionally inclusing logs, reports,...)
seal5_flow.export(...)
# Optional: Cleanup all artifacts
seal5_flow.cleanup(...)
```

### Command-Line Interface

Command line interface is aligned with the Python API. See `examples/demo.sh` for an full usage example

```sh
export SEAL5_HOME=...
seal5 --dir $SEAL5_HOME reset  --settings
seal5 init [--non-interactive] [-c]
seal5 load --files ...
seal5 setup ...
seal5 transform ...
seal5 generate ...
seal5 patch ...
seal5 build ...
seal5 test ...
seal5 deploy ...
seal5 export ...
seal5 clean [--temp] [--patches] [--models] [--inputs]
```

## Examples

See [`examples/demo.py`](https://github.com/tum-ei-eda/seal5/blob/main/examples/demo.py) for example of end-to-end flow!

## Documentation

Checkout [Seal5's ReadTheDocs Page](https://seal5.readthedocs.io/en/latest/?version=latest)!

## Limitations

See [here](https://github.com/tum-ei-eda/seal5/blob/main/LIMITATIONS.md).

## CI/CD Flow

We added a (manual) CI job to run the `examples/demo.py` script via GitHub actions.

## Contributions

Seal5 issue tracker: https://github.com/tum-ei-eda/seal5/issues

CoreDSL2LLVM/PatternGen issue tracker: https://github.com/mathis-s/CoreDSL2LLVM/issues

## References

N/A

## Acknowledgment

<img src="./BMBF_gefoerdert_2017_en.jpg" alt="drawing" height="75" align="left" >

This research is partially funded by the German Federal Ministry of Education and Research (BMBF) within
the projects [Scale4Edge](https://www.edacentrum.de/scale4edge/) (grant number 16ME0465) and [MANNHEIM-FlexKI](https://www.edacentrum.de/projekte/MANNHEIM-FlexKI) (grant number 01IS22086L).
