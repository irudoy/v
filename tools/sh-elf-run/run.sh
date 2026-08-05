#!/bin/sh
set -eu

tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$tool_dir/../.." && pwd)
image_name=${VQ_SH_ELF_IMAGE:-vq-sh-elf-run:16.3}
npkern_source=${VQ_NPKERN_SOURCE:-$repo_root/../../oss/npkern}

if [ ! -d "$npkern_source" ]; then
    echo "npkern source directory is missing: $npkern_source" >&2
    exit 1
fi
npkern_source=$(CDPATH= cd -- "$npkern_source" && pwd)

if [ "${VQ_SH_ELF_SKIP_BUILD:-0}" != "1" ]; then
    docker build --tag "$image_name" "$tool_dir"
fi
docker run --rm \
    --mount "type=bind,src=$repo_root,dst=/workspace,readonly" \
    "$image_name" "$@"
docker run --rm \
    --entrypoint python3 \
    --mount "type=bind,src=$repo_root,dst=/workspace,readonly" \
    --mount "type=bind,src=$npkern_source,dst=/npkern,readonly" \
    "$image_name" \
    /workspace/tools/sh-elf-run/verify_npkern_can.py /npkern "$@"
