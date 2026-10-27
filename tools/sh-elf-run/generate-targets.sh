#!/bin/sh
set -eu

tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$tool_dir/../.." && pwd)
image_name=${VQ_SH_ELF_IMAGE:-vq-sh-elf-run:16.3}

DOCKER_CONTEXT=default
export DOCKER_CONTEXT
unset DOCKER_HOST

inputs_label=$(python3 "$tool_dir/image_inputs.py")
docker build --tag "$image_name" --label "$inputs_label" "$tool_dir"
docker run --rm \
    --mount "type=bind,src=$repo_root,dst=/workspace" \
    --entrypoint python3 \
    "$image_name" \
    tools/sh-elf-run/generate_runtime_targets.py "$@"
