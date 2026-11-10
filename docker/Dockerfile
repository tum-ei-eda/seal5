ARG BASE_IMAGE="ubuntu:20.04"

FROM ${BASE_IMAGE} AS seal5-deps
LABEL maintainer "Seal5 Developers"
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update \
    && apt-get -qq -y install --no-install-recommends git wget unzip vim openssh-client ca-certificates \
    python3 python3-pip python3-venv virtualenv python3-dev python3-pip python3-setuptools \
    cmake make ninja-build build-essential \
    ccache \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/ \
    && rm -rf /var/cache/apt/lists


# Install modern CMake
ARG ENABLE_CMAKE="true"
ARG CMAKE_REPO="https://github.com/Kitware/CMake"
ARG CMAKE_VERSION="3.22.2"
ARG CMAKE_TARGET="Linux-x86_64"
RUN if [ "${ENABLE_CMAKE}" = "true" ] ; \
    then \
    cd /tmp \
    && apt-get remove cmake -yy -q \
    && wget -O cmake.sh ${CMAKE_REPO}/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-${CMAKE_TARGET}.sh \
    && mkdir -p /opt/cmake/ \
    && sh ./cmake.sh --skip-license --exclude-subdir --prefix=/opt/cmake/ \
    && rm ./cmake.sh ; \
    fi
ENV PATH="/opt/cmake/bin/:/usr/lib/ccache/:$PATH"
# ENV PATH="/opt/cmake/bin/:$PATH"
# RUN /usr/sbin/update-ccache-symlinks

CMD ["/bin/bash"]

FROM seal5-deps AS seal5-base

ADD . /seal5
WORKDIR /seal5
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH=/seal5
RUN . /venv/bin/activate && pip install --upgrade pip --no-cache-dir
RUN . /venv/bin/activate && pip install -r requirements.txt --no-cache-dir
RUN . /venv/bin/activate && pip install . --no-cache-dir

CMD ["seal5"]

ARG LLVM_REPO="https://github.com/llvm/llvm-project.git"
ARG LLVM_REF="llvmorg-19.1.7"
ARG CLONE_DEPTH=1
FROM seal5-base AS seal5-quickstart
WORKDIR /seal5

ENV SEAL5_HOME="/seal5_llvm"
ENV LLVM_REPO=${LLVM_REPO}
ENV LLVM_REF=${LLVM_REF}
ENV PREPATCHED=1
ENV RESET=0
ENV INIT=0
ENV SETUP=0
ENV SEAL5_HOME="/seal5_llvm"

RUN . /venv/bin/activate && seal5 --verbose --dir ${SEAL5_HOME} init --non-interactive --clone --clone-url ${LLVM_REPO} --clone-ref ${LLVM_REF} --clone-depth ${CLONE_DEPTH}
RUN . /venv/bin/activate && seal5 --verbose load --overwrite --files /seal5/examples/common/cfg/filter.yml /seal5/examples/common/cfg/git.yml /seal5/examples/common/cfg/llvm.yml /seal5/examples/common/cfg/patches.yml /seal5/examples/common/cfg/riscv.yml /seal5/examples/common/cfg/tools.yml
RUN . /venv/bin/activate && seal5 --verbose setup
RUN . /venv/bin/activate && seal5 --verbose patch -s 0
RUN . /venv/bin/activate && seal5 --verbose build --ccache

CMD ["seal5"]
