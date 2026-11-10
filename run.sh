#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${ROOT_DIR}/scripts/build.sh"
SAVED_TTY="$(stty -g 2>/dev/null || true)"
cleanup_terminal() {
    if [[ -n "${SAVED_TTY}" ]]; then stty "${SAVED_TTY}" 2>/dev/null || true; fi
    printf '\033[0m\033[?25h\033[?1049l'
}
trap cleanup_terminal EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
env -u NO_COLOR MLANG_FORCE_ANSI=1 "${ROOT_DIR}/build/mlarkanoid" "$@"
