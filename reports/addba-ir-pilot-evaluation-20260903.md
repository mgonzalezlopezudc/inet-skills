# ADDBA feature IR pilot evaluation

## Outcome

The Phase 5 pilot demonstrates that a single non-authoritative `feature.yaml` can connect reviewed
standards evidence to protocol roles, atomic obligations, state transitions, frame exchanges, INET
symbols, and focused tests without committing IEEE source text. The pilot should proceed to the
Phase 6 authority-and-location decision, but the generated manifest must not yet become canonical
project policy.

The strongest evidence of value is diagnostic: the manifest makes successful setup traceable while
keeping refusal, response timeout, and normal DELBA initiation visibly incomplete or disputed. A
prose summary would tend to blur those different conclusions.

## Evaluated inputs

- Standards corpus: format 2, fresh, generated from IEEE Std 802.11-2024 source SHA-256
  `c08beb0e16bf8c36465a331d349dd8b8ea79b28d4a320288312ddeb5ce8d9bb1`.
- INET checkout: `/home/user/omnetpp_ws/inet-pr-doc-project` at
  `61c17cfa70558b4e1ff2788f475e22a016ea0302` with a clean tracked worktree.
- Tool checkout baseline: `d578819bb7e554ee82499afad654f538715bd66a` plus the uncommitted Phase 1–5 work.
- Source-derived artifact: ignored
  `standards/processed/spec-pilot/addba/feature.yaml` in the INET checkout.
- Committed-safe evidence: the schema, validator, CLI, synthetic fixture, tests, and this report;
  none contains substantial verbatim IEEE text.

The pilot intentionally covers ordinary, single-TID immediate Block Ack setup between capable
non-DMG HT peers, refusal, a response-timeout hypothesis, and DELBA termination. Specialized S1G,
DMG, EDMG, GCR, BAT, NDP, multi-TID, unsolicited, modification, SAR, and buffer-sizing behavior is
explicitly excluded.

## Manifest and validator results

The generated manifest contains:

| Item | Count |
| --- | ---: |
| Reviewed source nodes/spans | 9 |
| Roles | 2 |
| Conditions | 16 |
| Actions | 10 |
| Qualifiers | 8 |
| Atomic obligations | 12 |
| State variables / transitions | 2 / 10 |
| Exchanges / invariants | 5 / 3 |
| Implementation mappings | 16 |
| Verification mappings | 4 |
| Source-check passes | 2 |

Obligation status remains split across three independent axes:

| Axis | Result |
| --- | --- |
| Source review | 11 `source-checked`, 1 `disputed` |
| Implementation | 4 `implemented`, 8 `mapped` |
| Verification | 4 `covered`, 8 `uncovered`, 0 `verified` |

Every source locator and reviewed span hash resolves against the current corpus. Every resolved INET
path, symbol, test configuration, and selector resolves against the checkout. The implementation
mappings classify four targets as realizing their obligation, eight as partial, three as
contradicting it, and one as an explicit gap. Three of the four verification mappings are explicit
coverage gaps.

The validator also enforces the properties that made the pilot reviewable:

- the authority marker is always `non-authoritative`;
- semantic identifiers are descriptive slugs rather than sequence numbers;
- every obligation has exactly one action and at least one canonical source node/span/hash;
- role, condition, action, qualifier, transition, invariant, mapping, and review links resolve;
- implementation and verification mappings are bidirectional;
- `mapped`, `implemented`, `covered`, and `verified` statuses require matching evidence;
- resolved source, code, and test targets are checked when their roots are supplied;
- exactly two source-check passes are present, and pass two records an omission, qualification, or
  disagreement.

## Source review findings

The first pass extracted the ordinary setup, explicit success/refusal split, response correlation,
and both DELBA directions from exact structural nodes. The second pass changed the result in four
important ways:

1. Specialized Block Ack variants were recorded as exclusions instead of being generalized into the
   ordinary exchange.
2. Peer capability, TID, dialog token, and response status remain independent conditions.
3. Agreement modification was excluded because its TID and replacement semantics differ from
   initial setup.
4. The response-timeout outcome remains disputed. The 2024 corpus exposes a deprecated MIB timeout
   attribute but no identified setup-procedure node defining what happens to pending agreement
   state. The manifest therefore labels the transition `derived` and `disputed` rather than
   presenting it as an IEEE obligation.

## INET and test gaps exposed by the pilot

- Recipient refusal is not implemented: `RecipientBlockAckAgreementPolicy::isAddbaReqAccepted()`
  always accepts, so no non-success response path is reachable.
- Originator response validation is incomplete:
  `OriginatorBlockAckAgreementPolicy::isAddbaReqAccepted()` always accepts and does not check status
  or dialog-token correlation. The handler lookup does constrain the peer and TID.
- Response construction relies on default values rather than explicitly copying the request dialog
  token and setting the negotiated status.
- Response timeout is not implemented:
  `OriginatorBlockAckAgreementPolicy::computeAddbaFailureTimeout()` throws an unimplemented error.
- The normal no-data/final-exchange DELBA trigger has no mapped implementation. Frame construction
  and sent/received cleanup handlers do exist.
- `N_BlockAck.test` reaches the production success path and observes later BlockAckReq/BlockAck
  traffic, so four setup obligations are `covered`. It does not directly assert response fields or
  agreement states, and no mapped test covers refusal, response timeout, or DELBA. Nothing is marked
  `verified`.

These are evaluation findings only. Phase 5 does not authorize or implement INET behavior changes.

## Reproducible checks

No INET rebuild was required because Phase 5 changed only Python tooling, synthetic fixtures,
documentation, and an ignored YAML artifact.

From `/home/user/omnetpp_ws/inet-skills`:

```bash
python3 -m unittest discover -s python/inet/spec -p 'test_*.py' -v
```

From `/home/user/omnetpp_ws/inet-pr-doc-project`:

```bash
../inet-skills/bin/inet_spec validate \
  --feature standards/processed/spec-pilot/addba/feature.yaml \
  --corpus standards/processed \
  --inet-root . --json

../inet-skills/bin/inet_spec trace \
  originator-abandons-pending-setup-after-timeout \
  --feature standards/processed/spec-pilot/addba/feature.yaml \
  --corpus standards/processed \
  --inet-root . --json
```

The focused suite passes 25 tests. Both real-pilot commands exit successfully with no validation
warnings; the timeout trace exposes the disputed source, contradicting implementation stub, and
missing module-test mapping in one result.

## Productization gate

Recommendation: pass the value gate and proceed to the Phase 6 design decision, subject to these
constraints:

1. Decide the permanent INET location and who may approve a manifest before moving this ignored
   artifact into project-controlled source.
2. Keep the source-derived IR explicitly non-authoritative until that decision is recorded.
3. Resolve the response-timeout source question against an exact applicable revision before using it
   to drive code or tests.
4. Treat the implementation and coverage gaps above as separate future changes with their own
   standards citations and focused protocol/module tests.
5. Do not add a discoverable feature-specification skill until the permanent workflow is approved;
   Mermaid and other views remain generated outputs.
