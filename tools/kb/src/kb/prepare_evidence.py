"""Independently prepare one validated local receipt without publishing it."""

import argparse
import hashlib
from pathlib import Path

from kb import copy_witness, local_paths, lock, repo, sid22_witness, test_evidence

PREFIX = 'kb-evidence-prepared '


def prepare(protocol, process, stdout, stderr, output, *, candidate=None, root=repo.ROOT):
    root = Path(root).resolve()
    output = local_paths.owned(output, root).resolve()
    if not output.resolve().is_relative_to(local_paths.results_root(root)) or output.exists():
        raise ValueError('a fresh preparation output inside tmp/local-results is required')
    with lock.held(root):
        if protocol == 'CAN':
            record = copy_witness.prepare(process, stdout, stderr, root)
        elif protocol == 'SID22':
            record = sid22_witness.prepare(process, stdout, stderr, root)
        elif protocol == 'TEST':
            if candidate is None:
                raise ValueError('TEST preparation requires its actual candidate')
            record = test_evidence.prepare(candidate, process, stdout, stderr, root)
        else:
            raise ValueError('unknown evidence protocol')
        # This destination is a job artifact, not a native receipt.
        data = (test_evidence.json_text(record) + '\n').encode()
        test_evidence.publish(output, record)
        if output.read_bytes() != data:
            raise ValueError('the validated preparation output changes before completion')
    return hashlib.sha256(data).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', choices=('CAN', 'SID22', 'TEST'))
    parser.add_argument('--process', required=True)
    parser.add_argument('--stdout', required=True)
    parser.add_argument('--stderr', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--candidate')
    args = parser.parse_args(argv)
    identity = prepare(args.protocol, args.process, args.stdout, args.stderr,
                       args.output, candidate=args.candidate)
    print(PREFIX + 'protocol=' + args.protocol + ' sha256=' + identity, flush=True)


if __name__ == '__main__':
    main()
