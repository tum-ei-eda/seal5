# Docker Images for Seal5

## Prerequisites

In addition to a regular Docker installation, `buildx` is required for building the Seal5 images.

```sh
sudo apt install docker-buildx-plugin
```

## Container/Image Types

### Deps

The `seal5-deps` image is an Ubuntu images with all the operating system packages required by Seal5 and its dependencies.

### Base

The `seal5-base` image contains an installation of the Seal5 Python package with all dependencies. Use this if you want to initialize your own `SEAL5_HOME` on a host directory mounted within the container.

### Quickstart

The image `seal5-quickstart` builds up on the user `seal5-base` image by initializing and installing a specific environment on it. The defined LLVM version is cloned and the initial (`STAGE_0`) Seal5 passes already applied. This offers the fastest experience which should produce a patched LLVM version within a few minutes. The `SEAL5_HOME` has to be located inside the container, build artifacts can be accessed via docker volumes/mount points (see below).

## Usage

### Pulling prebuilt images

Check our DockerHub for the latest images and supported OS/LLVM versions:

- [`tumeda/seal5-deps`](https://hub.docker.com/r/tumeda/seal5-deps/tags)
  - Ubuntu 20.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-deps/latest-default-ubuntu-20.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-deps/latest-default-ubuntu-20.04)
  - Ubuntu 22.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-deps/latest-default-ubuntu-22.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-deps/latest-default-ubuntu-22.04)
  - Ubuntu 24.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-deps/latest-default-ubuntu-24.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-deps/latest-default-ubuntu-24.04)
- [`tumeda/seal5-base`](https://hub.docker.com/r/tumeda/seal5-base/tags)
  - Ubuntu 20.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-base/latest-default-ubuntu-20.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-base/latest-default-ubuntu-20.04)
  - Ubuntu 22.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-base/latest-default-ubuntu-22.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-base/latest-default-ubuntu-22.04)
  - Ubuntu 24.04 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-base/latest-default-ubuntu-24.04) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-base/latest-default-ubuntu-24.04)
- [`tumeda/seal5-quickstart`](https://hub.docker.com/r/tumeda/seal5-quickstart/tags)
  - Ubuntu 20.04
    - LLVM 18.1.8 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-20.04-llvmorg-18.1.8) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-20.04-llvmorg-18.1.8)
    - LLVM 19.1.7 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-20.04-llvmorg-19.1.7) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-20.04-llvmorg-19.1.7)
  - Ubuntu 22.04
    - LLVM 18.1.8 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-22.04-llvmorg-18.1.8) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-22.04-llvmorg-18.1.8)
    - LLVM 19.1.7 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-22.04-llvmorg-19.1.7) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-22.04-llvmorg-19.1.7)
  - Ubuntu 24.04
    - LLVM 18.1.8 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-24.04-llvmorg-18.1.8) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-24.04-llvmorg-18.1.8)
    - LLVM 19.1.7 ![Docker Image Version (tag)](https://img.shields.io/docker/v/tumeda/seal5-quickstart/latest-default-ubuntu-24.04-llvmorg-19.1.7) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/tumeda/seal5-quickstart/latest-default-ubuntu-24.04-llvmorg-19.1.7)

Example Commands:

```sh
docker pull tumeda/seal5-deps:latest-default-ubuntu-20.04
docker pull tumeda/seal5-base:latest-default-ubuntu-20.04
docker pull tumeda/seal5-quickstart:latest-default-ubuntu-20.04-llvmorg-19.1.7
```

### Building images

#### Command line (local)

You can build the images as follows:

```sh
# Execute from top level of repository

# Build seal5-deps image
docker buildx build . -f docker/Dockerfile --tag tumeda/seal5-deps:latest-default-ubuntu-20.04 --target seal5-deps --build-arg BASE_IMAGE=ubuntu:20.04

# Build seal5-base image
docker buildx build . -f docker/Dockerfile --tag tumeda/seal5-base:latest-default-ubuntu-20.04 --target seal5-base --build-arg BASE_IMAGE=ubuntu:20.04

# Build seal5-quickstart image (takes a long time)
docker buildx build . -f docker/Dockerfile --tag tumeda/seal5-quickstart:latest-default-ubuntu-20.04-llvmorg-19.1.7 --target seal5-quickstart --build-arg BASE_IMAGE=ubuntu:20.04 --build-arg LLVM_REF="llvmorg-19.1.7"
```

Build times (excluding pulling of base image) on 18-core workstation:

- `seal5-deps`: 56s
- `seal5-base`: 71s full, 25s incremental
- `seal5-quickstart`: 1054s full, 984s incremental

Image sizes:

- `seal5-deps`: `723MB`
- `seal5-base`: `895MB`
- `seal5-quickstart`: `8.91GB`

#### Via GitHub Actions (online)

**Manual builds**

Use the `Run Workflow` button on https://github.com/tum-ei-eda/seal5/actions/workflows/container.yml to build images for a specific OS & LLVM version.

**CI Setup for DockerHub**

If you want to use the actions on a fork, they will fail due to missing docker credentials. Please export the followinf variables via `Settings -> Secrets -> Actions` to tell the jobs about your username and password:

- `DOCKER_PASSWORD`
- `DOCKER_USERNAME` (i.e. `tumeda`)
- `DOCKER_REGISTRY` (i.e. `docker.io`, `ghcr.io`)
- `DOCKER_NAMESPACE` (i.e. `tumeda`, `path/to/container`)

### Running the Images in Docker Containers

To use the previously built images, run the following commands

```sh
# seal5-base
docker run -it --rm -v $(pwd):$(pwd) -v /tmp/seal5_llvm:/seal5_llvm tumeda/seal5-base seal5 --dir /seal5_llvm wrapper $(pwd)/examples/example/cdsl/Example.core_desc $(pwd)/examples/common/cfg/patches.yml $(pwd)/examples/common/cfg/git.yml $(pwd)/examples/common/cfg/llvm.yml $(pwd)/examples/common/cfg/filter.yml

# seal5-quickstart
docker run -it --rm -v $(pwd):$(pwd) -v /tmp/seal5_out:/out tumeda/seal5-quickstart seal5 wrapper $(pwd)/examples/example/cdsl/Example.core_desc --out /out
```

Depending on the types of patches being applied and the system used for running the containers, the `seal5-quickstart` image can generate a prebuilt & patched LLVM in just a few minutes (210s on an 18-core workstation).
