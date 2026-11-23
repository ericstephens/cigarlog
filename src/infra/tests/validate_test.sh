#!/usr/bin/env bash
# infra/tests/validate_test.sh
# Runs `tofu init -backend=false` and `tofu validate` in the infra/ directory.
# Exits non-zero with a clear message on failure; prints "PASS: tofu validate" on success.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${INFRA_DIR}"

echo "INFO: Running tofu init -backend=false in ${INFRA_DIR}"
if ! tofu init -backend=false -input=false -no-color; then
  echo "FAIL: tofu init failed" >&2
  exit 1
fi

echo "INFO: Running tofu validate"
if ! tofu validate -no-color; then
  echo "FAIL: tofu validate failed" >&2
  exit 1
fi

echo "PASS: tofu validate"
