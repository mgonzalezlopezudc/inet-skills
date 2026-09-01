#!/usr/bin/env bash
# Skill-local mechanical checks that are not implemented by doc/project/enforcement/check-architecture.sh.
# The rule text and exception ledger remain canonical under doc/project/.

set -uo pipefail

if [ "$#" -gt 1 ]; then
  echo "usage: $0 [src/inet/<subtree>]" >&2
  exit 2
fi

SCOPE="${1:-src/inet}"
SCOPE="${SCOPE#./}"
SCOPE="${SCOPE%/}"
if [[ "$SCOPE" != "src/inet" && "$SCOPE" != src/inet/* ]]; then
  echo "error: scope must be src/inet or one of its subtrees: '$SCOPE'" >&2
  exit 2
fi
if [ ! -d "$SCOPE" ]; then
  echo "error: '$SCOPE' not found (run from the INET repository root)" >&2
  exit 2
fi

intersect_scope() {
  local canonical="$1"
  local requested="$2"
  if [[ "$requested" == "$canonical" || "$requested" == "$canonical"/* ]]; then
    printf '%s\n' "$requested"
  elif [[ "$canonical" == "$requested"/* ]]; then
    printf '%s\n' "$canonical"
  fi
}

status=0
APP_SCOPE="$(intersect_scope "src/inet/applications" "$SCOPE")"

if [ -n "$APP_SCOPE" ]; then
  echo "== AR-COM-SOCKETS: $APP_SCOPE =="
  app_hits=$(grep -rEn --include='*.h' --include='*.cc' --include='*.icc' \
    '^[[:space:]]*#[[:space:]]*include[[:space:]]+"inet/transportlayer/[^/"[:space:]]+/' \
    "$APP_SCOPE" 2>/dev/null | grep -vE '/transportlayer/(contract|common)/' || true)
  if [ -n "$app_hits" ]; then
    echo "$app_hits" | sed 's/^/  CANDIDATE: /'
    status=1
  else
    echo "  ok"
  fi
else
  echo "== AR-COM-SOCKETS: N/A (scope does not intersect src/inet/applications) =="
fi

echo
echo "== AR-QUAL-DETERMINISM: $SCOPE =="
DET_PATTERN='std::random_device|std::chrono::|(^|[^[:alnum:]_])rand[[:space:]]*\(|(^|[^[:alnum:]_])time[[:space:]]*\([[:space:]]*(NULL|nullptr|0)?[[:space:]]*\)'
DET_ALLOW='src/inet/common/ResultFilters\.cc:[0-9]+:[[:space:]]*(startTime = time\(nullptr\);|time_t t = time\(nullptr\);)'
det_hits=$(grep -rEn --include='*.h' --include='*.cc' --include='*.icc' "$DET_PATTERN" "$SCOPE" 2>/dev/null \
  | grep -vE "/visualizer/|/thirdparty/|/external/|$DET_ALLOW" || true)
if [ -n "$det_hits" ]; then
  echo "$det_hits" | sed 's/^/  CANDIDATE: /'
  status=1
else
  echo "  ok"
fi

echo
if [ "$status" -eq 0 ]; then
  echo "PASS: additional architecture checks clean."
else
  echo "FAIL: candidates above require reconciliation with doc/project/audit/architecture-exceptions.md."
fi
exit "$status"
