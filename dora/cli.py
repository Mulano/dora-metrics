"""Usage: python -m dora.cli data/sample_deployments.csv"""
import json
import sys

from .metrics import load_csv, summarize


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    print(json.dumps(summarize(load_csv(sys.argv[1])), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
