"""License guard — refuse RED-license dependencies in pyproject.toml.

Used as a pre-commit hook and as a CI step. The RED list is the union of
``DEFAULT_RED_NAMES`` (hardcoded for fast CI) and any names parsed from the
``RED (商用 OSS 不可)`` section of ``THIRD_PARTY_NOTICES.md`` (single source
of truth for license claims). When the notices file lists a name not in
``DEFAULT_RED_NAMES``, the parsed set still blocks installs.
"""

from __future__ import annotations

import argparse
import re
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
    "flow-matching",
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
    "facebookresearch-memory",
}


def _flatten_deps(pyproject_data: dict) -> list[str]:
    out: list[str] = []
    project = pyproject_data.get("project", {})
    out.extend(project.get("dependencies", []))
    for _, extras in (project.get("optional-dependencies") or {}).items():
        out.extend(extras)
    return out


def _pkg_name(spec: str) -> str:
    # Strip at the earliest occurrence of any separator (not the first
    # separator in iteration order — that orderswas the previous bug).
    seps = [">=", "<=", "==", "~=", "!=", ">", "<", " ", "[", ";", "@"]
    found = [spec.find(s) for s in seps]
    positions = [i for i in found if i != -1]
    if not positions:
        return spec.strip().lower()
    return spec[: min(positions)].strip().lower()


_RED_BULLET_RE = re.compile(r"^\s*[-*]\s+\*\*([A-Za-z0-9_.\-/]+)\*\*")


def _parse_red_from_notices(text: str) -> set[str]:
    """Pick names out of the RED section of THIRD_PARTY_NOTICES.md.

    Strategy: locate the RED heading, then collect bullet labels until the
    next top-level section heading. Names are slug-normalized (lowercase
    plus `/` → `-`). Best-effort — the hardcoded ``DEFAULT_RED_NAMES`` is
    always enforced regardless of parse success.
    """
    lines = text.splitlines()
    out: set[str] = set()
    in_red = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("###"):
            in_red = "RED" in stripped
            continue
        if stripped.startswith("##") and not stripped.startswith("###"):
            in_red = False
            continue
        if not in_red:
            continue
        m = _RED_BULLET_RE.match(line)
        if m:
            raw = m.group(1).lower().replace("/", "-")
            out.add(raw)
    return out


def _collect_red_names() -> set[str]:
    red = set(DEFAULT_RED_NAMES)
    if NOTICES.exists():
        try:
            red |= _parse_red_from_notices(NOTICES.read_text(encoding="utf-8"))
        except OSError:
            pass
    return red


def check(red_names: set[str] | None = None) -> int:
    if not PYPROJECT.exists():
        print(f"license_guard: {PYPROJECT} not found", file=sys.stderr)
        return 2
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    deps = _flatten_deps(data)
    red = red_names if red_names is not None else _collect_red_names()
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
    parser.add_argument("--list-red", action="store_true", help="print the resolved RED name list")
    args = parser.parse_args(argv)
    if args.list_red:
        for n in sorted(_collect_red_names()):
            print(n)
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
