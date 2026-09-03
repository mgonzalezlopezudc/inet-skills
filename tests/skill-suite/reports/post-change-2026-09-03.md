# Skill-suite post-change evaluation — 2026-09-03

This reruns the baseline case IDs as a static frontmatter and workflow audit after the routing,
regression, verification, maintenance, and history changes. Two positive/negative pairs were added
for the new generic regression and `opp_repl` skills. No live model runner was available, so turns,
tokens, runtime, and observed dynamic loads remain explicitly `NOT_RUN`.

## Before and after

| Metric | Baseline | Post-change | Method |
| --- | ---: | ---: | --- |
| Activation accuracy | 45 / 46 (97.8%) | 50 / 50 (100%) | Manual audit against frontmatter selection contracts |
| Workflow correctness | 7 / 7 | 7 / 7 | Required semantic gates in the unchanged workflow cases |
| Routing acceptance | 4 / 6 | 6 / 6 | Same six routing case IDs and gates |
| Unnecessary skill loads | 1 | 0 | Orchestration no longer selected for localized or wide mechanical single-agent work |
| Turns | NOT_RUN | NOT_RUN | Requires platform evaluation runner |
| Tokens | NOT_RUN | NOT_RUN | Requires platform token accounting |
| Runtime | NOT_RUN | NOT_RUN | Requires platform timing around the same corpus |

The original orchestration activation failure now selects the localized authoring path. The wide
rename now selects the mechanical invariant path. One-line or wide behavioral changes both select
the semantic contract path. Sealing, pre-write contract, focused verification, approval, and
independent-review gates remain in that path.

## Added coverage and maintenance outcomes

- Protocol-neutral regression design now owns claim → invariant → category → minimal reproduction →
  direct evidence → bounded campaign. The Wi-Fi specialization owns only WLAN invariants,
  standards/feature gates, and packet-exchange evidence.
- Schema v1 and fact-only adapters cover unit, module, fingerprint, and `opp_repl` results, including
  pass, assertion failure, build/runner error, zero selection, malformed output, and an approved
  expected baseline change.
- Platform metadata is generated from `.agents/skill-suite.yaml`; `--check` rejects drift.
- The orphan review reference was removed after its checks were confirmed in the maintained layered
  references.
- Deployment packaging excludes `__pycache__` and `*.pyc`. The default profile excludes the
  walkthrough skill while its analyzer capability files are absent.
- Shared `inet-opp-repl` mechanics replace duplicated runner/dependency/result guidance, while
  cleanup and rebase retain separate authorization and history guarantees.

## Remaining capability limits

- Live activation/turn/token/runtime measurements still require a platform evaluation runner.
- The walkthrough profile remains unavailable in this INET checkout because the analyzer and its
  README are absent.
- `opp_scavetool` remains unavailable on this shell's `PATH`; result analysis requires an activated
  OMNeT++ environment.
- Performance analysis remains deferred because no recurring demand record or maintenance owner was
  found.
