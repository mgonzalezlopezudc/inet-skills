#!/usr/bin/env bash
#
# Check if any modified or target files overlap with sealed paths in INET.
# Reference: sealing-status.md and sealing.md
#
# Usage (from the INET repository root or skill directory):
#   bash check-sealing.sh [file1 file2 ...]
#   bash check-sealing.sh --diff           # check git working tree and staged diff
#   bash check-sealing.sh --staged         # check staged changes only
#
# Exit status:
#   0 = All target files are unsealed (or no files provided)
#   1 = One or more target files are SEALED (explicit approval required)
#   2 = Error (e.g. sealing-status.md not found)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATUS_FILE="${SCRIPT_DIR}/../sealing-status.md"

if [ ! -f "$STATUS_FILE" ]; then
  # Fallback search if called from elsewhere
  STATUS_FILE="$(find . -name "sealing-status.md" | head -n 1)"
fi

if [ -z "$STATUS_FILE" ] || [ ! -f "$STATUS_FILE" ]; then
  echo "error: sealing-status.md not found." >&2
  exit 2
fi

# Extract sealed patterns from sealing-status.md
# Matches lines like: - 🔒 `common/packet/` *(recursive)*
SEALED_PATTERNS=()
while IFS= read -r line; do
  if [[ "$line" =~ \`([^\`]+)\` ]]; then
    pattern="${BASH_REMATCH[1]}"
    SEALED_PATTERNS+=("$pattern")
  fi
done < <(awk '
  /<!--/ { in_comment = 1 }
  !in_comment && /^[[:space:]]*-[[:space:]]*🔒/ { print }
  /-->/ { in_comment = 0 }
' "$STATUS_FILE")

if [ ${#SEALED_PATTERNS[@]} -eq 0 ]; then
  echo "info: No sealed paths found in $STATUS_FILE. All files unsealed."
  exit 0
fi

# Collect target files
TARGET_FILES=()

if [ $# -eq 0 ] || [ "${1:-}" = "--diff" ]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    while IFS= read -r -d '' f; do
      TARGET_FILES+=("$f")
    done < <(git diff --name-only -z HEAD 2>/dev/null)
    while IFS= read -r -d '' f; do
      TARGET_FILES+=("$f")
    done < <(git ls-files --others --exclude-standard -z 2>/dev/null)
  fi
elif [ "${1:-}" = "--staged" ]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    while IFS= read -r -d '' f; do
      TARGET_FILES+=("$f")
    done < <(git diff --name-only -z --cached 2>/dev/null)
  fi
else
  for arg in "$@"; do
    TARGET_FILES+=("$arg")
  done
fi

if [ ${#TARGET_FILES[@]} -eq 0 ]; then
  echo "info: No files to check."
  exit 0
fi

sealed_hits=0

for file in "${TARGET_FILES[@]}"; do
  # Normalize path relative to src/inet/
  norm_file="$file"
  if [[ "$norm_file" == src/inet/* ]]; then
    norm_file="${norm_file#src/inet/}"
  elif [[ "$norm_file" == */src/inet/* ]]; then
    norm_file="${norm_file#*/src/inet/}"
  fi

  # An exact .msg seal also covers its generated C++ siblings even when the generated file is
  # passed directly. Directory seals already cover both source and generated paths.
  source_msg=""
  if [[ "$norm_file" == *_m.h ]]; then
    source_msg="${norm_file%_m.h}.msg"
  elif [[ "$norm_file" == *_m.cc ]]; then
    source_msg="${norm_file%_m.cc}.msg"
  fi

  for pattern in "${SEALED_PATTERNS[@]}"; do
    if [[ "$pattern" == */ ]]; then
      # Directory pattern (recursive)
      dir_prefix="${pattern%/}"
      if [[ "$norm_file" == "$dir_prefix"/* ]] || [[ "$norm_file" == "$dir_prefix" ]]; then
        echo "🔒 SEALED: '$file' matches sealed directory '$pattern'"
        sealed_hits=$((sealed_hits + 1))
        break
      fi
    else
      # Exact file pattern
      if [[ "$norm_file" == "$pattern" || ( -n "$source_msg" && "$source_msg" == "$pattern" ) ]]; then
        if [[ "$norm_file" == "$pattern" ]]; then
          echo "🔒 SEALED: '$file' matches sealed file '$pattern'"
        else
          echo "🔒 SEALED: '$file' is generated from sealed message file '$pattern'"
        fi
        sealed_hits=$((sealed_hits + 1))
        break
      fi
    fi
  done
done

echo
if [ "$sealed_hits" -gt 0 ]; then
  echo "GUARD VIOLATION: $sealed_hits file(s) are SEALED under src/inet/."
  echo "STOP: You must obtain explicit user permission in this conversation before modifying sealed files."
  exit 1
else
  echo "GUARD PASSED: All checked files are unsealed. Proceeding is safe."
  exit 0
fi
