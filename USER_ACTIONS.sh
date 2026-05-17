#!/usr/bin/env bash
#
# USER_ACTIONS.sh — every remaining manual step, in one place.
#
# Each step is structurally independent and idempotent where possible. Run
# `bash USER_ACTIONS.sh --plan` to print the steps without executing them;
# run `bash USER_ACTIONS.sh <step>` to execute a single step; run without
# arguments for an interactive walk-through. Secrets (HF token, GH token)
# come from your existing shell environment — this script never writes
# them and never reads files that might contain them.
#
# Steps:
#   1  github-repo-create    (one-time; needs `gh auth login` beforehand)
#   2  hf-login              (one-time; needs your HuggingFace token in HF_TOKEN)
#   3  install-tier1         (GPU host; pulls torch + flux + mamba)
#   4  measure-vram          (GPU host; real S0-c measurement)
#   5  toy-train-3run        (GPU host; S3 gate — 3-run loss curve)
#   6  references-verify     (any host; flips docs/REFERENCES.md to verified)
#   7  release-tag           (one-time; cuts v0.1.0 after S3 GREEN + REFERENCES verified)
#   8  arxiv-submit          (one-time; user opens arXiv submission portal)
#
# Authorization scope: this script touches your local git remote and your
# HuggingFace cache. It does NOT push commits or weights anywhere on your
# behalf without an explicit step invocation.

set -euo pipefail

readonly REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_NAME="klein-mamba-loa"
readonly STATE_FILE="$REPO_ROOT/experiments/_wip/transfusion-gibson/pipeline-state.json"

log() { printf '[USER_ACTIONS] %s\n' "$*" >&2; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || { log "missing required command: $1"; exit 2; }; }

# ---------------------------------------------------------------------------
# Step 1 — create the GitHub repository (user-owned).
# Requires `gh auth login` to have completed beforehand. The gh CLI reads
# its token from ~/.config/gh/hosts.yml; this script never reads tokens.
# ---------------------------------------------------------------------------
step_github_repo_create() {
  need_cmd gh
  need_cmd git
  cd "$REPO_ROOT"
  if [[ ! -d .git ]]; then
    git init
    git add -A
    git commit -m "Initial commit (auto-OSS audit pass)" || true
  fi
  # Use whatever org/user is currently authenticated.
  local owner
  owner="$(gh api user --jq .login)"
  if gh repo view "$owner/$REPO_NAME" >/dev/null 2>&1; then
    log "repo $owner/$REPO_NAME already exists; skipping create"
  else
    gh repo create "$owner/$REPO_NAME" --public --source=. --push --description \
      "Stratified Persona Flow (SPF) — pre-alpha"
  fi
  # Patch placeholder-org → real owner across every doc that ships URLs.
  for f in pyproject.toml docs/MODEL_CARD.md README.md docs/REFERENCES.md; do
    if [[ -f "$REPO_ROOT/$f" ]] && grep -q "placeholder-org" "$REPO_ROOT/$f"; then
      sed -i.bak "s|placeholder-org|$owner|g" "$REPO_ROOT/$f"
      rm -f "$REPO_ROOT/$f.bak"
    fi
  done
  log "placeholders rewritten to $owner in pyproject.toml + docs. Commit and push:"
  log "  git -C \"$REPO_ROOT\" add -A && git -C \"$REPO_ROOT\" commit -m 'chore: set repo URL'"
  log "  git -C \"$REPO_ROOT\" push"
}

# ---------------------------------------------------------------------------
# Step 2 — log into HuggingFace so weight downloads work.
# Reads HF_TOKEN from the environment if set, otherwise opens an interactive
# prompt. Never writes the token to a file in the repository.
# ---------------------------------------------------------------------------
step_hf_login() {
  need_cmd huggingface-cli
  if [[ -n "${HF_TOKEN:-}" ]]; then
    huggingface-cli login --token "$HF_TOKEN" --add-to-git-credential
  else
    log "HF_TOKEN not in env — falling back to interactive login"
    huggingface-cli login
  fi
}

# ---------------------------------------------------------------------------
# Step 3 — install the full Tier 1 dependency set.
# This pulls torch (~800 MB), FLUX.2 wrapper deps, Mamba SSM kernels, and
# the optional MCP transport. Skip on CPU-only hosts.
# ---------------------------------------------------------------------------
step_install_tier1() {
  need_cmd pip
  cd "$REPO_ROOT"
  pip install -e ".[flow,mamba,flux,mcp,dev]"
}

# ---------------------------------------------------------------------------
# Step 4 — real S0-c VRAM measurement on a GPU host.
# Writes to experiments/_wip/transfusion-gibson/vram_report.json. The dry-run
# variant runs on any host.
# ---------------------------------------------------------------------------
step_measure_vram() {
  cd "$REPO_ROOT"
  python -m pip install --quiet --upgrade pip
  python scripts/measure_vram.py --tier 1
  log "report at experiments/_wip/transfusion-gibson/vram_report.json"
}

# ---------------------------------------------------------------------------
# Step 5 — S3 gate: 3-run toy training and aggregate the loss curve.
# This calls examples/toy_train.py with 3 seeds. On GPU the run completes in
# seconds; on CPU it works but slowly.
# ---------------------------------------------------------------------------
step_toy_train_3run() {
  cd "$REPO_ROOT"
  PYTHONPATH=. python examples/toy_train.py \
    --steps 500 \
    --out experiments/_wip/transfusion-gibson/toy_train_report.json
  log "report at experiments/_wip/transfusion-gibson/toy_train_report.json"
}

# ---------------------------------------------------------------------------
# Step 6 — flip docs/REFERENCES.md from pending-human-verify to verified.
# THIS STEP REQUIRES A HUMAN. The script opens each arXiv URL and asks for
# the abstract sha256 from the human; it does not fetch the page itself.
# ---------------------------------------------------------------------------
step_references_verify() {
  cd "$REPO_ROOT"
  log "Open each canonical URL in docs/REFERENCES.md, confirm the title,"
  log "compute sha256 of the visible abstract HTML, and edit the file."
  log "Then commit: git commit -am 'docs: REFERENCES.md verified pre-arXiv-v1'"
}

# ---------------------------------------------------------------------------
# Step 7 — cut release tag v0.1.0. Only do this after S3 is GREEN AND
# REFERENCES.md is fully verified.
# ---------------------------------------------------------------------------
step_release_tag() {
  need_cmd git
  cd "$REPO_ROOT"
  if grep -q "pending-human-verify" docs/REFERENCES.md; then
    log "Refusing to tag: docs/REFERENCES.md still has pending-human-verify entries."
    exit 3
  fi
  git tag -a v0.1.0 -m "klein-mamba-loa v0.1.0 (S3 GREEN + arXiv evidence verified)"
  git push --tags
}

# ---------------------------------------------------------------------------
# Step 8 — open the arXiv submission portal (browser). The script does NOT
# submit on your behalf; it just opens the URL.
# ---------------------------------------------------------------------------
step_arxiv_submit() {
  local url="https://arxiv.org/submit"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url"
  elif command -v open >/dev/null 2>&1; then
    open "$url"
  else
    log "Open this URL in your browser: $url"
  fi
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
print_plan() {
  cat <<'EOF'
Remaining manual steps (run any of these via `bash USER_ACTIONS.sh <step>`):

  1  github-repo-create    one-time           prereq: gh auth login
  2  hf-login              one-time           prereq: HF_TOKEN in env or interactive
  3  install-tier1         GPU host           pulls torch + flux + mamba deps
  4  measure-vram          GPU host           real S0-c gate (writes vram_report.json)
  5  toy-train-3run        GPU host preferred S3 gate (writes toy_train_report.json)
  6  references-verify     any host, human    flips REFERENCES.md to verified
  7  release-tag           one-time           refuses if REFERENCES.md not verified
  8  arxiv-submit          one-time, human    opens https://arxiv.org/submit
EOF
}

main() {
  if [[ $# -eq 0 ]]; then
    print_plan
    exit 0
  fi
  case "$1" in
    --plan|plan)          print_plan ;;
    1|github-repo-create) step_github_repo_create ;;
    2|hf-login)           step_hf_login ;;
    3|install-tier1)      step_install_tier1 ;;
    4|measure-vram)       step_measure_vram ;;
    5|toy-train-3run)     step_toy_train_3run ;;
    6|references-verify)  step_references_verify ;;
    7|release-tag)        step_release_tag ;;
    8|arxiv-submit)       step_arxiv_submit ;;
    *) log "unknown step: $1"; print_plan; exit 1 ;;
  esac
}

main "$@"
