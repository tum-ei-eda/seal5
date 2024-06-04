# Seal5


[![pypi package](https://badge.fury.io/py/seal5.svg)](https://pypi.org/project/seal5)
[![readthedocs](https://readthedocs.org/projects/seal5/badge/?version=latest)](https://seal5.readthedocs.io/en/latest/?version=latest)
[![GitHub license](https://img.shields.io/github/license/tum-ei-eda/seal5.svg)](https://github.com/tum-ei-eda/seal5/blob/main/LICENSE)

[![demo workflow](https://github.com/tum-ei-eda/seal5/actions/workflows/demo.yml/badge.svg)](https://github.com/tum-ei-eda/seal5/actions/workflows/demo.yml)

TODO: Summary

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

Install all required python packages using the follow8n* command:

`pip install -r requirements.txt`.

For development (linting, packaging,...) there are a few more dependencies which can be installed via:

`pip install -r requirements_dev.txt`.

### Installation

**Warning:** It is highly recommended to install `seal5` into a new virtual environment. Follow these steps to initialize and enter a venv in your seal5 repo directory:

```sh
# alternative: python3 -m venv venv
virtualenv -p python3.8 venv
source venv/bin/activate
```

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
# Archive final LLVM (optionally inclusing logs, reports,...)
seal5_flow.export(...)
# Optional: Cleanup all artifacts
seal5_flow.cleanup(...)
```

### Command-Line Interface

TODO: Not yet implemented...

## Examples

See [`examples/demo.py`](examples/demo.py) for example of end-to-end flow!

## Documentation

TODO: Sphinx Documentation / GitHub Pages

## Limitations

See [here](./LIMITATIONS.md).

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
