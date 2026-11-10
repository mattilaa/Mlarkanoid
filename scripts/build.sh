#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MLANG_ROOT="${MLANG_ROOT:-${ROOT_DIR}/../mlang}"
if [[ -z "${MLANG:-}" ]]; then
    if [[ -x "${HOME}/.local/bin/mlang" ]]; then
        MLANG="${HOME}/.local/bin/mlang"
    else
        MLANG="mlang"
    fi
fi
export MLANG_STDLIB_PATH="${MLANG_STDLIB_PATH:-${MLANG_ROOT}/stdlib}"
export MLANG_MODULE_PATH="${ROOT_DIR}/src${MLANG_MODULE_PATH:+:${MLANG_MODULE_PATH}}"
if [[ ! -f "${MLANG_STDLIB_PATH}/std/esc.mla" ]]; then
    echo "Cannot find std::esc in ${MLANG_STDLIB_PATH}; set MLANG_ROOT to your mlang checkout." >&2
    exit 1
fi
mkdir -p "${ROOT_DIR}/build"
cd "${ROOT_DIR}"
if [[ "${1:-}" == "test" ]]; then
    "${MLANG}" test tests -Wno-colon-if
else
    "${MLANG}" -Wno-colon-if src/main.mla -o build/mlarkanoid
fi
