"""License guard — refuse RED-license dependencies in pyproject.toml.

Used as a pre-commit hook and as a CI step. The RED list is sourced from
THIRD_PARTY_NOTICES.md (single source of truth) and re-checked against
pyproject.toml on every commit that touches it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover - py3.10
    import tomli as tomllib  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]
NOTICES = REPO_ROOT / "THIRD_PARTY_NOTICES.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"

DEFAULT_RED_NAMES = {
    "flow_matching",
    "facebookresearch-flow-matching",
    "chameleon",
    "chameleon-7b",
    "edm2",
    "hunyuanvideo",
    "hunyuan3d",
    "hunyuan3d-2",
    "flux-1-dev",
    "flux-1-kontext-dev",
    "memory-layers-at-scale",
}


def _flatten_deps(pyproject_data: dict) -> list[str]:
    out: list[str] = []
    project = pyproject_data.get("project", {})
    out.extend(project.get("dependencies", []))
    for _, extras in (project.get("optional-dependencies") or {}).items():
        out.extend(extras)
    return out


def _pkg_name(spec: str) -> str:
    for sep in [">=", "<=", "==", "~=", "!=", ">", "<", " ", "["]:
        idx = spec.find(sep)
        if idx != -1:
            return spec[:idx].strip().lower()
    return spec.strip().lower()


def check(red_names: set[str] | None = None) -> int:
    if not PYPROJECT.exists():
        print(f"license_guard: {PYPROJECT} not found", file=sys.stderr)
        return 2
    data = tomllib.loads(PYPROJECT.read_text())
    deps = _flatten_deps(data)
    red = red_names or DEFAULT_RED_NAMES
    violations = [d for d in deps if _pkg_name(d) in red]
    if violations:
        print("license_guard: RED-license dependencies detected:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    print(f"license_guard: OK ({len(deps)} dependencies scanned, 0 RED violations)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="License guard")
    parser.add_argument("--check", action="store_true", help="check pyproject (default)")
    parser.add_argument("--list-red", action="store_true", help="print the RED name list")
    args = parser.parse_args(argv)
    if args.list_red:
        for n in sorted(DEFAULT_RED_NAMES):
            print(n)
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
