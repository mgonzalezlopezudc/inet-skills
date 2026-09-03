# Rebase failure recovery and adaptation

Read this reference only after an attempt reports `FAIL` or `ERROR`, or when a conflict requires a
semantic adaptation.

Compare the attempt with every applicable role in `opp-repl-contract.md`: original topic, stage
anchor, valid plain-upstream stage, and previous group/integration safe point. Explain the first
causal divergence rather than the final symptom.

Preserve the failed attempt and create a fresh attempt branch. Represent each semantic adaptation as
a new fix commit. If mechanical conflict resolution must be folded into a replayed commit, record
that fact and the adapted source SHA using the same durable fix schema.

An adaptation is a production change. Use `inet-code-authoring`; resolve architecture, naming,
exception-ledger, and seal obligations with `inet-architectural-requirements` for semantic
`src/inet/` scope. Rebase authorization does not authorize an unrelated redesign or any baseline
update. Re-run the same scoped check before and after so the evidence remains comparable.

For each adaptation, record:

1. fix SHA/subject or folded-conflict marker and adapted topic commit;
2. first build/test/configuration/run failure before the fix;
3. the same check after the fix, including any accepted residual difference;
4. the upstream/topic interaction and restored contract that make the fix correct;
5. authoring, architecture, sealing, verification, review, baseline, and user approvals.

Obtain human approval before promoting an adapted attempt. On persistent failure, stop with bounded
choices such as checkpoint subdivision, group split/merge, integration-mode revision, or human-led
investigation. Do not broaden scope, discard history, or rewrite a baseline merely to obtain a safe
point.
