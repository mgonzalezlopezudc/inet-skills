#!/usr/bin/env bash
#
# Starter architecture check for INET — a T3 fitness function (see AR-QUAL-ENFORCED).
# Enforces two dependency-direction rules from architectural-requirements.md over the
# C++ #include graph:
#
#   AR-ORG-DOMAINS   — the shared 'common' package must not depend on any protocol layer
#                      (dependencies point protocols -> infrastructure, never the reverse)
#   AR-ORG-VIS-SPLIT — model/protocol code must not depend on the visualizer package
#   AR-COM-SOCKETS   — applications must communicate with transport via socket contracts,
#                      not by directly #including internal protocol implementation headers
#   AR-QUAL-DET      — model/simulation code must not use non-deterministic time or RNG
#                      (std::chrono, time(), rand(), std::random_device)
#
# Usage (from the INET repository root):
#   doc/tmp/enforcement/check-architecture.sh            # full check
#   doc/tmp/enforcement/check-architecture.sh <SUBTREE>  # scope checks to a subset,
#                                                        # e.g. src/inet/common/packet
#
# With no argument, checks cover their canonical scopes across src/inet.
# A SUBTREE argument restricts all checks to that directory.
#
# Exit status 0 = clean, 1 = violations found. Wire it into CI to make the rule a gate.
# This is intentionally a grep-level starter; a robust version would parse the full
# include graph (e.g. dependency-cruiser / a small Python tool) and check for cycles.

set -uo pipefail
SCOPE="${1:-}"
if [ -n "$SCOPE" ]; then
  DOMAIN_SCOPE="$SCOPE"; VIS_SCOPE="$SCOPE"; APP_SCOPE="$SCOPE"; DET_SCOPE="$SCOPE"
else
  DOMAIN_SCOPE="src/inet/common"; VIS_SCOPE="src/inet"; APP_SCOPE="src/inet/applications"; DET_SCOPE="src/inet"
fi
status=0

for d in "$DOMAIN_SCOPE" "$VIS_SCOPE"; do
  if [ ! -d "$d" ]; then
    echo "error: '$d' not found (run from the INET repo root)" >&2
    exit 2
  fi
done

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

echo "== AR-ORG-DOMAINS: $DOMAIN_SCOPE must not #include a protocol layer (foundational value types allowlisted) =="
hits=$(grep -rEn "#include \"inet/(${LAYERS})/" "$DOMAIN_SCOPE" 2>/dev/null | grep -vE "$ALLOW" || true)
if [ -n "$hits" ]; then
  echo "$hits" | sed 's/^/  VIOLATION: /'
  echo "  ^ common/ reaches up into a protocol layer — invert the dependency (AR-EXT-ATTACH),"
  echo "    or record a sanctioned exception in architecture-exceptions.md."
  status=1
else
  echo "  ok"
fi

echo
echo "== AR-ORG-VIS-SPLIT: non-visualizer code must not #include visualizer/ =="
if hits=$(grep -rEln "#include \"inet/visualizer/" "$VIS_SCOPE" 2>/dev/null | grep -v "/visualizer/"); then
  echo "$hits" | sed 's/^/  VIOLATION: /'
  echo "  ^ model/protocol code depends on the visualizer — visualizers must subscribe from outside."
  status=1
else
  echo "  ok"
fi

if [ -d "$APP_SCOPE" ]; then
  echo
  echo "== AR-COM-SOCKETS: applications must not #include internal transport implementation headers =="
  # Applications must use contract/ socket APIs (e.g. TcpSocket.h, UdpSocket.h), not internal engine headers
  if app_hits=$(grep -rEn "#include \"inet/transportlayer/(tcp|udp|sctp)/" "$APP_SCOPE" 2>/dev/null | grep -v "/contract/" || true); then
    if [ -n "$app_hits" ]; then
      echo "$app_hits" | sed 's/^/  VIOLATION: /'
      echo "  ^ application directly couples to transport internals — use socket contracts (*Socket.h)."
      status=1
    else
      echo "  ok"
    fi
  else
    echo "  ok"
  fi
fi

if [ -d "$DET_SCOPE" ]; then
  echo
  echo "== AR-QUAL-DET: model code must not use non-deterministic time or RNG =="
  # Exclude visualizers, external/thirdparty, and tests if scoped broadly
  det_hits=$(grep -rEn "\b(std::random_device|std::chrono::|(?<![a-zA-Z0-9_])rand\(|(?<![a-zA-Z0-9_])time\(\s*NULL|\btime\(\s*nullptr|\btime\(\s*0)\b" "$DET_SCOPE" 2>/dev/null | grep -vE "/visualizer/|/thirdparty/|/external/" || true)
  if [ -n "$det_hits" ]; then
    echo "$det_hits" | sed 's/^/  VIOLATION: /'
    echo "  ^ non-deterministic time or RNG detected — use OMNeT++ simTime(), cRNG, or RNG streams."
    status=1
  else
    echo "  ok"
  fi
fi

echo
if [ "$status" -eq 0 ]; then
  echo "PASS: architecture checks clean."
else
  echo "FAIL: architecture violations found (record permanent exceptions, fix the rest)."
fi
exit "$status"
