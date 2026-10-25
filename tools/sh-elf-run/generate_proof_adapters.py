"""Generate standard bounded adapter sources without executing firmware inputs."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/kb/src'))
from kb import proof_adapter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = {}
    for path in proof_adapter.DESCRIPTORS:
        if args.write:
            result[path] = proof_adapter.write_generated(ROOT, path)
        else:
            proof_adapter.require_generated(ROOT, path)
            result[path] = {name: proof_adapter.digest(data)
                for name, data in proof_adapter.generated(ROOT, path).items()}
    print(json.dumps(dict(schema=1, mode='write' if args.write else 'check',
        source_generation_only=True, firmware_execution=False, generated=result), sort_keys=True))


if __name__ == '__main__':
    main()
