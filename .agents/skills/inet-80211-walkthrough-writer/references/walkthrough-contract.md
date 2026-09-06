# IEEE 802.11 walkthrough contract

Project-level documentation and evidence obligations come from the active project guidance discovered
through the shared procedure. This reference adds the analyzer-owned walkthrough format.

## Goal

Teach one feature and show what the current example proves.

This contract applies only after the capability and placement gate in the owning `SKILL.md` passes.
The analyzer's historical location does not override the active checkout's canonical distinction
among examples, showcases, and tutorials.

## Evidence vocabulary

| Status | Meaning |
|---|---|
| `PASS` | Direct relevant evidence satisfies the claim in the stated scope. |
| `FAIL` | Direct evidence contradicts the claim or a required check failed. |
| `INCONCLUSIVE` | Evidence exists, but a decisive control, field, or correlation is missing. |
| `NOT RUN` | No retained evidence exists for the check. |

Call configuration an input, script output a derived measurement, decoded
fields/results a direct observation, and unsupported causal explanation an
inference.

## Ownership

- Prefix level-2 through level-6 headings with `[author]` or `[script]`.
- `[script]` headings and all analysis tables, plots, and frame exchanges must
  be inside analysis-script generated blocks.
- Authors preserve generated blocks and the script-owned results-session
  ledger. Authors update only the separate `[author]` session line.
- Use `NOT RECORDED` only for legacy evidence and `NOT RUN` only when no
  evidence was executed.

Place the ledger immediately below the title:

```text
<!-- BEGIN SCRIPT RESULTS SESSIONS -->
`[script]` results sessions:

- Scalar/vector: `<session-id-or-NOT-RUN>`
- PCAP: `<session-id-or-NOT-RUN>`
<!-- END SCRIPT RESULTS SESSIONS -->

`[author]` results sessions: `<session-id-or-NOT-RECORDED>`.
```

## Required content

Keep the canonical headings used by the template, but keep sections short.

- **Primer:** Explain the problem, roles, decisive frames/state, and expected
  exchange in plain language.
- **Scenario:** State topology, traffic, causal configuration difference, and
  why the setup exposes the feature. Link only relevant NED/INI files.
- **Standards/model boundary:** Cite exact IEEE material for normative claims.
  Separate the standard, INET abstraction, requested configuration, and
  observed behavior.
- **Evidence status:** List each central claim, status, authoritative
  script-generated output, run/seed scope, and gap.
- **Configuration matrix:** Show only the control/treatment delta and material
  confounders.
- **Invariants/diagnostics:** Give an observable check, failure symptom, and
  first focused diagnostic.
- **Reproduction:** Give the repository working directory and exact analyzer
  commands/session. Include direct simulation commands only when they were
  actually used for diagnosis.
- **Scalar/vector analysis:** Preserve the script-generated plot/table block.
  Explain the question it answers, the main result, uncertainty, and limits.
- **PCAP statistics:** Preserve the script-generated plot/table block. Explain
  relevant packet composition, counting/capture semantics, and limits.
- **Frame exchange:** Preserve the script-generated timeline/table. Explain
  the decisive sequence and fields without restating every row.
- **Verdict:** Connect configuration, mechanism evidence, packet exchange, and
  outcome. Scope each `PASS`, `FAIL`, or `INCONCLUSIVE` claim.
- **Limitations:** List only gaps that could change the verdict and the
  smallest useful next check.

Generated analysis content is authoritative presentation output. Never
hand-create an analysis table or plot, run a separate query to fill one in, or
copy generated rows into authored prose. If scripts cannot generate a needed
view, record the gap and improve the shared analysis machinery.

Use repository-relative artifact links; do not publish absolute `/home` paths. Keep population
claims scoped to the sampled runs and event-level causal claims within one results session.
