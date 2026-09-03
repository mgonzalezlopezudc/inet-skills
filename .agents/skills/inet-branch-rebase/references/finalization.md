# Rebase target assembly and finalization

Read this reference after every current group reaches pinned `main`.

1. Assemble the clean target from pinned `main`, each non-dropped topic effect in approved order,
   and every accepted adaptation effect. Exclude stage-only scaffolding. Keep an adaptation separate
   only when it is an independently valid prerequisite before its first consumer; otherwise fold it
   into the causal rebased commit while retaining the forensic attempt that proved it. If this
   re-authoring exceeds approval, obtain authorization or hand off to `inet-branch-cleanup`.
2. Prove one-to-one approved commit coverage and order. Confirm every recorded attempt, integration,
   and safe-point branch still resolves to its immutable SHA.
3. Check out and test every final target commit with its directly applicable build/test scope, then
   run the final union contract from `opp-repl-contract.md`. A later repair does not excuse an
   unusable earlier commit. Use original topic and pinned plain upstream as controls where they
   distinguish intended upstream movement from regression.
4. Use `inet-pull-request-authoring` to audit commit boundaries, order, messages, per-commit evidence,
   and final branch narrative under the applicable `PR-*` rules.
5. Run `doc/project/guide/run-the-gates.md` only when publication is requested. For local-only
   delivery, record that publication gates were not run and do not publish.
6. Complete the state-log finalization with target SHA, group/stage completion, exact per-commit and
   union envelopes, every explained delta, adaptation provenance, final audit, and residual risks.

Request final delivery approval. Draft or publish a pull request only when the user explicitly asks
for that additional action.
