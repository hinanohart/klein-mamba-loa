"""Sub-R14 trigger guard — refuse Python files exceeding 500 LOC.

Blueprint section 7's sub-R14 trigger ("> 500 LOC OR module-crossing
structural change") was previously a human promise. This script makes
the 500-LOC half machine-checkable; the module-crossing half remains
a reviewer judgment call.

Used as a pre-commit hook and a CI step. Counts physical lines in
``klein_mamba_loa/`` and ``scripts/``; ignores blank lines and lines
that are only a comment (consistent with the spirit of "implementation
density").
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["klein_mamba_loa", "scripts"]
CAP = 500


def count_code_lines(path: Path) -> int:
    total = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        total += 1
    return total


def main() -> int:
    violations: list[tuple[Path, int]] = []
    for d in SCAN_DIRS:
        for py in sorted((REPO_ROOT / d).rglob("*.py")):
            n = count_code_lines(py)
            if n > CAP:
                violations.append((py.relative_to(REPO_ROOT), n))
    if violations:
        print("check_file_lengths: files exceeding sub-R14 cap:", file=sys.stderr)
        for p, n in violations:
            print(f"  {p}: {n} code lines (> {CAP})", file=sys.stderr)
        return 1
    print(f"check_file_lengths: OK (cap = {CAP} code lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
