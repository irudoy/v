#!/bin/sh
set -eu

tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$tool_dir/../.." && pwd)
image_name=${VQ_SH_ELF_IMAGE:-vq-sh-elf-run:16.3}
with_npkern=0

if [ "${1:-}" = "--with-npkern" ]; then
    with_npkern=1
    shift
fi

# Use the standard local Docker context independently of the caller's active
# context.
DOCKER_CONTEXT=default
export DOCKER_CONTEXT
unset DOCKER_HOST

if [ "${VQ_SH_ELF_SKIP_BUILD:-0}" != "1" ]; then
    docker build --tag "$image_name" "$tool_dir"
fi
docker run --rm \
    --mount "type=bind,src=$repo_root,dst=/workspace,readonly" \
    "$image_name" "$@"

if [ "$with_npkern" -eq 1 ]; then
    "$tool_dir/run-npkern.sh" "$@"
else
    echo "NPKERN_CAN_VERIFY status=SKIP reason=not_requested external_gate=true hardware_ready=NO"
fi
