#!/usr/bin/env bash
# Publish the artifact to GitHub: repository, branch, freeze tag, release.
#
#   gh auth login          # once, interactively -- this script cannot do it
#   bash tools/publish.sh
#
# Idempotent: safe to re-run. It never force-pushes and never rewrites history.

set -euo pipefail

REPO_NAME="gc-ir-reference"
DESCRIPTION="GC-IR Reference Implementation — reproducibility artifact for \"From Risk Register to Runtime Predicate\""
FREEZE_TAG="preregister-tier0-v1"
RELEASE_TAG="v1.0.0"

cd "$(dirname "$0")/.."

echo "==> Checking authentication"
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh is not authenticated. Run this once, interactively:"
  echo ""
  echo "    gh auth login"
  echo ""
  exit 1
fi
gh auth status 2>&1 | sed 's/^/    /'

OWNER="$(gh api user --jq .login)"
echo "==> Authenticated as ${OWNER}"

echo "==> Checking the working tree is clean"
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: working tree is not clean. Commit or stash first:"
  git status --short
  exit 1
fi

echo "==> Verifying the freeze before publishing"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
"$PY" -m experiments.verify_freeze

echo "==> Creating or reusing the remote repository"
if gh repo view "${OWNER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "    ${OWNER}/${REPO_NAME} already exists; reusing it"
else
  gh repo create "${OWNER}/${REPO_NAME}" --public --description "${DESCRIPTION}"
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "    remote 'origin' already set to $(git remote get-url origin)"
else
  git remote add origin "https://github.com/${OWNER}/${REPO_NAME}.git"
fi

echo "==> Pushing main"
git push -u origin main

echo "==> Pushing the preregistration freeze tag (this is what makes the commitment public)"
git push origin "refs/tags/${FREEZE_TAG}"

echo "==> Re-verifying: the public commitment should now be discharged"
"$PY" -m experiments.verify_freeze --write results/final/freeze_verification.json

echo "==> Tagging and pushing the release"
if git rev-parse -q --verify "refs/tags/${RELEASE_TAG}" >/dev/null; then
  echo "    ${RELEASE_TAG} already exists locally"
else
  git tag -a "${RELEASE_TAG}" -m "GC-IR Reference Implementation ${RELEASE_TAG}

Reference implementation and empirical artifact for \"From Risk Register to
Runtime Predicate\". Measured results in results/final/SUMMARY.md; manuscript
reconciliation in paper_update/.

Preregistration freeze: ${FREEZE_TAG}"
fi
git push origin "refs/tags/${RELEASE_TAG}"

echo "==> Creating the GitHub release"
if gh release view "${RELEASE_TAG}" >/dev/null 2>&1; then
  echo "    release ${RELEASE_TAG} already exists"
else
  gh release create "${RELEASE_TAG}" \
    --title "GC-IR Reference Implementation v1.0.0" \
    --notes-file docs/RELEASE_NOTES_v1.0.0.md \
    MANIFEST.sha256 \
    preregistration/FREEZE_MANIFEST.sha256 \
    results/final/SUMMARY.md
fi

echo ""
echo "==> Published: https://github.com/${OWNER}/${REPO_NAME}"
echo "==> Freeze tag: https://github.com/${OWNER}/${REPO_NAME}/releases/tag/${FREEZE_TAG}"
echo "==> Release:    https://github.com/${OWNER}/${REPO_NAME}/releases/tag/${RELEASE_TAG}"
echo ""
echo "Remaining manual steps:"
echo "  1. Wait for the cross-platform determinism workflow, then:"
echo "       gh run download --name 'determinism-*' --dir downloaded"
echo "       ${PY} -m experiments.check_ci_agreement downloaded --out results/final/CI_STATUS.md"
echo "     Only after that may the determinism claim be scoped to 'the tested"
echo "     supported environments' (see paper_update/PLACEHOLDER_REPLACEMENT_TABLE.md B4)."
echo "  2. Zenodo archival: docs/ZENODO_RELEASE_STEPS.md. Do not cite a DOI until it exists."
