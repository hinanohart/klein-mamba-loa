"""License guard — refuse RED-license dependencies in pyproject.toml.

Used as a pre-commit hook and as a CI step. The RED list is the union of:

1. ``DEFAULT_RED_NAMES`` — hardcoded for fast CI startup and to immunise the
   guard against parser bugs.
2. Names parsed from the ``## RED`` section of ``THIRD_PARTY_NOTICES.md``
   (the documented single source of truth). When the notices file lists a
   name not in ``DEFAULT_RED_NAMES``, the parsed set still blocks installs.

The dependency-name comparison is done in PEP 503 canonical form (lowercase,
runs of ``[-_.]`` collapsed to ``-``) so ``flow_matching`` in pyproject and
``flow-matching`` in the notices both match.
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


def _canon(name: str) -> str:
    """PEP 503 canonicalisation: lower-case, runs of [-_.] → single '-'."""
    s = name.strip().lower()
    s = re.sub(r"[-_.\s]+", "-", s)
    return s.strip("-")


def _flatten_deps(pyproject_data: dict) -> list[str]:
    out: list[str] = []
    project = pyproject_data.get("project", {})
    out.extend(project.get("dependencies", []))
    for _, extras in (project.get("optional-dependencies") or {}).items():
        out.extend(extras)
    return out


def _pkg_name(spec: str) -> str:
    """Extract the package name from a PEP 508 dependency string."""
    seps = [">=", "<=", "==", "~=", "!=", ">", "<", " ", "[", ";", "@"]
    found = [spec.find(s) for s in seps]
    positions = [i for i in found if i != -1]
    raw = spec if not positions else spec[: min(positions)]
    return raw.strip().lower()


# Bullet structure: `- [bold|plain name] — license info`.
# We split on the first em-dash / en-dash / "--" sequence (with surrounding
# whitespace) to separate the *name field* from the license blurb.
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*[—–]\s+", re.UNICODE)
# Alternative: bullet without em-dash uses ` -- ` ASCII fallback.
_BULLET_DASH_RE = re.compile(r"^\s*[-*]\s+(.+?)\s+--\s+")
# Alias inside parens: e.g. "facebookresearch/memory (Memory Layers at Scale)".
_PAREN_RE = re.compile(r"\(([^)]+)\)")
# Skip tokens that are noise (license boilerplate, single short words).
_NOISE_TOKENS = {"and", "or", "the", "license", "see", "nvlabs"}


def _slugify(s: str) -> str:
    out = re.sub(r"[^A-Za-z0-9]+", "-", s.strip().lower()).strip("-")
    return out


def _is_useful(slug: str) -> bool:
    return len(slug) >= 3 and slug not in _NOISE_TOKENS


def _parse_red_from_notices(text: str) -> set[str]:
    """Extract RED-section package slugs from THIRD_PARTY_NOTICES.md.

    Robust to:
      * bold (`- **name**`) and plain (`- name`) bullet styles
      * em-dash (—), en-dash (–), and `--` separator forms
      * alternation via ``/`` ("FLUX.1-dev / FLUX.1-Kontext-dev")
      * parenthetical aliases ("facebookresearch/memory (Memory Layers at Scale)")

    All slugs are PEP-503 canonical (``flow_matching`` → ``flow-matching``).
    """
    out: set[str] = set()
    in_red = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            in_red = "RED" in line.upper()
            continue
        if line.startswith("### "):
            continue
        if not in_red:
            continue
        m = _BULLET_RE.match(raw) or _BULLET_DASH_RE.match(raw)
        if not m:
            continue
        name_part = m.group(1).strip().replace("**", "").strip()
        # 1. Parenthetical aliases stand alone.
        for paren in _PAREN_RE.findall(name_part):
            slug = _slugify(paren)
            if _is_useful(slug):
                out.add(slug)
        cleaned = _PAREN_RE.sub("", name_part).strip()
        # 2. Slash-alternation: each side is a candidate.
        sides = [side.strip() for side in re.split(r"\s*/\s*", cleaned) if side.strip()]
        for side in sides:
            slug = _slugify(side)
            if _is_useful(slug):
                out.add(slug)
        # 3. Full joined form ("facebookresearch/flow_matching"
        #     → "facebookresearch-flow-matching") matches DEFAULT entries.
        if len(sides) > 1:
            joined = _slugify(cleaned)
            if _is_useful(joined):
                out.add(joined)
    return out


def _collect_red_names() -> set[str]:
    red = {_canon(n) for n in DEFAULT_RED_NAMES}
    if NOTICES.exists():
        try:
            parsed = _parse_red_from_notices(NOTICES.read_text(encoding="utf-8"))
            red |= {_canon(n) for n in parsed}
        except OSError:
            pass
    return red


def check(red_names: set[str] | None = None) -> int:
    if not PYPROJECT.exists():
        print(f"license_guard: {PYPROJECT} not found", file=sys.stderr)
        return 2
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    deps = _flatten_deps(data)
    red_input = red_names if red_names is not None else _collect_red_names()
    red_canon = {_canon(n) for n in red_input}
    violations = [d for d in deps if _canon(_pkg_name(d)) in red_canon]
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
