#!/bin/sh
set -eu

tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$tool_dir/../.." && pwd)
image_name=${VQ_SH_ELF_IMAGE:-vq-sh-elf-run:16.3}
npkern_source=${VQ_NPKERN_SOURCE:-$repo_root/../../oss/npkern}
expected_revision=d364011963c1da59a907ca291e1c0602977e9fd0

DOCKER_CONTEXT=desktop-linux
export DOCKER_CONTEXT
unset DOCKER_HOST

if [ ! -d "$npkern_source" ]; then
    echo "NPKERN_CAN_VERIFY status=SKIP reason=source_missing source=$npkern_source expected_revision=$expected_revision external_gate=true hardware_ready=NO"
    exit 0
fi

npkern_source=$(CDPATH= cd -- "$npkern_source" && pwd)
actual_root=$(git -C "$npkern_source" rev-parse --show-toplevel)
actual_root=$(CDPATH= cd -- "$actual_root" && pwd)
if [ "$actual_root" != "$npkern_source" ]; then
    echo "NPKERN_CAN_VERIFY status=FAIL reason=source_root_mismatch source=$npkern_source git_root=$actual_root" >&2
    exit 1
fi

actual_revision=$(git -C "$npkern_source" rev-parse HEAD)
if [ "$actual_revision" != "$expected_revision" ]; then
    echo "NPKERN_CAN_VERIFY status=FAIL reason=revision_mismatch source=$npkern_source actual_revision=$actual_revision expected_revision=$expected_revision" >&2
    exit 1
fi

source_status=$(git -C "$npkern_source" status --porcelain --untracked-files=all)
if [ -n "$source_status" ]; then
    echo "NPKERN_CAN_VERIFY status=FAIL reason=source_dirty source=$npkern_source revision=$actual_revision" >&2
    exit 1
fi

if [ "${VQ_SH_ELF_SKIP_BUILD:-0}" != "1" ]; then
    docker build --tag "$image_name" "$tool_dir"
fi
docker run --rm \
    --entrypoint python3 \
    --mount "type=bind,src=$repo_root,dst=/workspace,readonly" \
    --mount "type=bind,src=$npkern_source,dst=/npkern,readonly" \
    "$image_name" \
    /workspace/tools/sh-elf-run/verify_npkern_can.py /npkern "$@"
