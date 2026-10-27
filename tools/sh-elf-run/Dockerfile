FROM debian:trixie-20261020-slim@sha256:62bd423aeee912639ca8ee681c2b762cb3e25137e0a92b20be455898a9f034ad AS toolchain

ARG DEBIAN_SNAPSHOT=20261026T082512Z
ARG DEBIAN_SECURITY_SNAPSHOT=20261026T044319Z
ARG BINUTILS_SH_ELF_VERSION=2.44+3+b1
ARG GCC_SH_ELF_VERSION=13.3.0-16+8.2+b3
ARG NEWLIB_SH_ELF_VERSION=4.4.0.20231231+8.2
ARG PYTHON3_VERSION=3.13.5-1
ARG PYTHON3_13_VERSION=3.13.5-2+deb13u5

# Every stage resolves packages from these fixed archive snapshots.
RUN printf '%s\n' \
        'Types: deb' \
        "URIs: http://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT}" \
        'Suites: trixie trixie-updates' \
        'Components: main' \
        'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' \
        'Check-Valid-Until: no' \
        '' \
        'Types: deb' \
        "URIs: http://snapshot.debian.org/archive/debian-security/${DEBIAN_SECURITY_SNAPSHOT}" \
        'Suites: trixie-security' \
        'Components: main' \
        'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' \
        'Check-Valid-Until: no' \
        > /etc/apt/sources.list.d/debian.sources

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        "binutils-sh-elf=${BINUTILS_SH_ELF_VERSION}" \
        "gcc-sh-elf=${GCC_SH_ELF_VERSION}" \
        "libnewlib-sh-elf-dev=${NEWLIB_SH_ELF_VERSION}" \
        "python3=${PYTHON3_VERSION}" \
        "python3.13=${PYTHON3_13_VERSION}" \
    && rm -rf /var/lib/apt/lists/*

RUN sha256sum /usr/bin/sh-elf-as /usr/bin/sh-elf-gcc /usr/bin/sh-elf-run \
    > /tmp/stock-toolchain.sha256

FROM toolchain AS observer-build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc g++ make bison flex texinfo xz-utils libgmp-dev patch \
    && rm -rf /var/lib/apt/lists/* \
    && sha256sum -c /tmp/stock-toolchain.sha256

ADD --checksum=sha256:bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5 \
    https://ftp.gnu.org/gnu/gdb/gdb-16.3.tar.xz /tmp/gdb.tar.xz
COPY gnu16.3-sh-pc-observer.patch /tmp/observer.patch

RUN mkdir -p /opt/src /opt/build /opt/gnu-sh-trace/bin \
    && tar -xJf /tmp/gdb.tar.xz -C /opt/src \
    && printf '%s  /opt/src/gdb-16.3/sim/sh/interp.c\n' \
        '973ac1c5d193af70a5f1b8f7f0f2a4bd6aec957a0a3533ec878e795dbab9eb10' \
        | sha256sum -c - \
    && cd /opt/src/gdb-16.3 \
    && patch --batch --fuzz=0 -p1 < /tmp/observer.patch \
    && printf '%s  /opt/src/gdb-16.3/sim/sh/interp.c\n' \
        '99f809d2a5c710a7d3fe3f97aa19ed92c8ad00bf5ed0a153384457e7a5fa3a42' \
        | sha256sum -c - \
    && cd /opt/build \
    && /opt/src/gdb-16.3/configure \
        --target=sh-elf --prefix=/opt/gnu-sh-trace \
        --disable-gdb --disable-gdbserver --disable-gas --disable-binutils \
        --disable-ld --disable-gprof --disable-gold --disable-nls --disable-werror \
        --without-guile --without-python --without-debuginfod \
        --enable-sim --enable-sim-trace=yes --enable-sim-debug=yes \
        --enable-sim-profile=yes \
    && make -j4 all-sim \
    && install -m755 sim/sh/run /opt/gnu-sh-trace/bin/sh-elf-run \
    && sha256sum -c /tmp/stock-toolchain.sha256

FROM toolchain

COPY --from=observer-build /opt/gnu-sh-trace /opt/gnu-sh-trace
RUN sha256sum -c /tmp/stock-toolchain.sha256 \
    && /opt/gnu-sh-trace/bin/sh-elf-run --version
ENV PATH="/opt/gnu-sh-trace/bin:${PATH}"

WORKDIR /workspace

ENTRYPOINT ["python3", "tools/sh-elf-run/verify_map_switching.py"]
