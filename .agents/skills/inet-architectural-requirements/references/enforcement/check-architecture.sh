#!/usr/bin/env bash
#
# Starter architecture check for INET — a T3 fitness function (see AR-QUAL-ENFORCED).
# Enforces focused dependency and determinism rules from architectural-requirements.md:
#
#   AR-ORG-DOMAINS   — the shared 'common' package must not depend on any protocol layer
#                      (dependencies point protocols -> infrastructure, never the reverse)
#   AR-ORG-VIS-SPLIT — model/protocol code must not depend on the visualizer package
#   AR-COM-SOCKETS   — applications must communicate with transport via socket contracts,
#                      not by directly #including internal protocol implementation headers
#   AR-QUAL-DETERMINISM — model/simulation code must not use non-deterministic time or RNG
#                      (std::chrono, time(), rand(), std::random_device)
#
# Usage (from the INET repository root):
#   bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh
#   bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh <SUBTREE>
#       # e.g. src/inet/common/packet
#
# With no argument, checks cover their canonical scopes across src/inet. A SUBTREE argument
# restricts general checks to that directory; rules with narrower canonical ownership run only
# on the intersection (common/ for AR-ORG-DOMAINS, applications/ for AR-COM-SOCKETS).
#
# Exit status 0 = clean, 1 = violations found. Wire it into CI to make the rule a gate.
# This is intentionally a grep-level starter. It does not parse the complete include graph or
# detect cycles, and reported source-pattern hits still require semantic reconciliation.

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

# Print the intersection of a canonical rule scope and the requested scope. An empty result means
# the focused subtree cannot contain a violation owned by that rule.
intersect_scope() {
  local canonical="$1"
  local requested="$2"
  if [[ "$requested" == "$canonical" || "$requested" == "$canonical"/* ]]; then
    printf '%s\n' "$requested"
  elif [[ "$canonical" == "$requested"/* ]]; then
    printf '%s\n' "$canonical"
  fi
}

DOMAIN_SCOPE="$(intersect_scope "src/inet/common" "$SCOPE")"
APP_SCOPE="$(intersect_scope "src/inet/applications" "$SCOPE")"
VIS_SCOPE="$SCOPE"
DET_SCOPE="$SCOPE"
status=0

LAYERS='physicallayer|linklayer|networklayer|transportlayer|routing|applications'

# Foundational value types that are depended on framework-wide. These are sanctioned
# exceptions (AS-* in architecture-exceptions.md) — ideally they would live in common/,
# but until they are moved, coupling to them is accepted rather than flagged.
ALLOW='networklayer/contract/ipv4/Ipv4Address\.h'
ALLOW+='|networklayer/contract/ipv6/Ipv6Address\.h'
ALLOW+='|networklayer/common/L3Address(Resolver)?\.h'
ALLOW+='|linklayer/common/MacAddress\.h'
ALLOW+='|linklayer/common/EtherType_m\.h'
ALLOW+='|networklayer/common/IpProtocolId_m\.h'

if [ -n "$DOMAIN_SCOPE" ]; then
  echo "== AR-ORG-DOMAINS: $DOMAIN_SCOPE must not #include a protocol layer (foundational value types allowlisted) =="
  hits=$(grep -rEn --include='*.h' --include='*.cc' --include='*.icc' "^[[:space:]]*#[[:space:]]*include[[:space:]]+\"inet/(${LAYERS})/" "$DOMAIN_SCOPE" 2>/dev/null | grep -vE "$ALLOW" || true)
  if [ -n "$hits" ]; then
    echo "$hits" | sed 's/^/  VIOLATION: /'
    echo "  ^ common/ reaches up into a protocol layer — invert the dependency (AR-EXT-ATTACH),"
    echo "    or record a sanctioned exception in architecture-exceptions.md."
    status=1
  else
    echo "  ok"
  fi
else
  echo "== AR-ORG-DOMAINS: N/A (focused scope does not intersect src/inet/common) =="
fi

echo
echo "== AR-ORG-VIS-SPLIT: non-visualizer code must not #include visualizer/ =="
if hits=$(grep -rEln --include='*.h' --include='*.cc' --include='*.icc' "^[[:space:]]*#[[:space:]]*include[[:space:]]+\"inet/visualizer/" "$VIS_SCOPE" 2>/dev/null | grep -v "/visualizer/"); then
  echo "$hits" | sed 's/^/  VIOLATION: /'
  echo "  ^ model/protocol code depends on the visualizer — visualizers must subscribe from outside."
  status=1
else
  echo "  ok"
fi

if [ -n "$APP_SCOPE" ]; then
  echo
  echo "== AR-COM-SOCKETS: applications must not #include internal transport implementation headers =="
  # Applications must use contract/ socket APIs (e.g. TcpSocket.h, UdpSocket.h), not internal engine headers
  app_hits=$(grep -rEn --include='*.h' --include='*.cc' --include='*.icc' "^[[:space:]]*#[[:space:]]*include[[:space:]]+\"inet/transportlayer/(tcp|udp|sctp)/" "$APP_SCOPE" 2>/dev/null | grep -v "/contract/" || true)
  if [ -n "$app_hits" ]; then
    echo "$app_hits" | sed 's/^/  VIOLATION: /'
    echo "  ^ application directly couples to transport internals — use socket contracts (*Socket.h)."
    status=1
  else
    echo "  ok"
  fi
else
  echo
  echo "== AR-COM-SOCKETS: N/A (focused scope does not intersect src/inet/applications) =="
fi

echo
echo "== AR-QUAL-DETERMINISM: model code must not use non-deterministic time or RNG =="
# Exclude visualization and vendored code; reviewers must distinguish simulation mechanics from
# legitimate non-simulation diagnostics in any remaining candidate hit.
DET_PATTERN='std::random_device|std::chrono::|(^|[^[:alnum:]_])rand[[:space:]]*\(|(^|[^[:alnum:]_])time[[:space:]]*\([[:space:]]*(NULL|nullptr|0)?[[:space:]]*\)'
# ElapsedTimeFilter deliberately records host elapsed time as a diagnostic result; it does not drive
# simulation mechanics. Keep this allowlist statement-specific so other wall-clock use in the same
# source file is still reported.
DET_ALLOW='src/inet/common/ResultFilters\.cc:[0-9]+:[[:space:]]*(startTime = time\(nullptr\);|time_t t = time\(nullptr\);)'
det_hits=$(grep -rEn --include='*.h' --include='*.cc' --include='*.icc' "$DET_PATTERN" "$DET_SCOPE" 2>/dev/null | grep -vE "/visualizer/|/thirdparty/|/external/|$DET_ALLOW" || true)
if [ -n "$det_hits" ]; then
  echo "$det_hits" | sed 's/^/  VIOLATION: /'
  echo "  ^ non-deterministic time or RNG candidate — use OMNeT++ simTime(), cRNG, or RNG streams"
  echo "    for simulation mechanics; reconcile legitimate diagnostic-only uses manually."
  status=1
else
  echo "  ok"
fi

echo
if [ "$status" -eq 0 ]; then
  echo "PASS: architecture checks clean."
else
  echo "FAIL: architecture violations found (record permanent exceptions, fix the rest)."
fi
exit "$status"
