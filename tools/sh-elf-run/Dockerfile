FROM debian:trixie-slim

ARG BINUTILS_SH_ELF_VERSION=2.44+3+b1
ARG GCC_SH_ELF_VERSION=13.3.0-16+8.2+b3
ARG NEWLIB_SH_ELF_VERSION=4.4.0.20231231+8.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        "binutils-sh-elf=${BINUTILS_SH_ELF_VERSION}" \
        "gcc-sh-elf=${GCC_SH_ELF_VERSION}" \
        "libnewlib-sh-elf-dev=${NEWLIB_SH_ELF_VERSION}" \
        python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ENTRYPOINT ["python3", "tools/sh-elf-run/verify_map_switching.py"]
