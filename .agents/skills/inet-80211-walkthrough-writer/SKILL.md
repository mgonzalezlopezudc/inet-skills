---
name: inet-80211-walkthrough-writer
description: Create, revise, or review INET IEEE 802.11 walkthroughs from current configuration and generated evidence. The active checkout must provide the shared analyzer and its README. Use for feature explanations with scalar/vector plots, PCAP statistics, tables, and frame exchanges. Do not invent or restore an absent analyzer workflow.
---

# Write IEEE 802.11 walkthroughs

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's project-level documentation and evidence obligations. This skill owns only the
IEEE 802.11 walkthrough contract and analyzer workflow.

Read [walkthrough-contract.md](references/walkthrough-contract.md) and [analysis-machinery.md](references/analysis-machinery.md). Start new documents from [walkthrough-template.md](assets/walkthrough-template.md).

## Capability and placement gate

Before a walkthrough edit:

1. Read the active checkout's project entry point.
   Follow its current repository-layout and documentation routes.
2. Verify that both `examples/ieee80211/analysis/wifi_analysis.py` and
   `examples/ieee80211/analysis/README.md` are tracked in the active checkout.
3. Verify that the requested document location matches the canonical distinction among examples,
   showcases, and tutorials. A measured argument with prose and charts belongs in `showcases/`, not
   `examples/`, unless the active project documents explicitly say otherwise.

If either analyzer file is absent, stop this workflow.
Also stop if the requested placement conflicts with the project documents.
Report that the checkout does not support the requested workflow.
Do not reconstruct the analyzer from Git history, ignored bytecode, generated artifacts, or skill text.

## Analysis boundary

Only `examples/ieee80211/analysis/wifi_analysis.py` and its suite-owned components may generate or publish:

- scalar/vector plots and tables;
- PCAP plots and statistics tables;
- frame-exchange timelines and tables.

Do not replace or supplement these outputs with `opp_scavetool`, TShark, ad hoc code, manual calculations, or hand-written tables.
Extend the shared analyzer when output is missing.
Preserve script-owned marker blocks and ledger entries.
Prose may interpret generated data but must not duplicate it.

## Workflow

1. Identify the example, configurations, current walkthrough, and generated sessions.
2. State one learning question and a small set of testable claims.
3. Use the shared analyzer to inspect the scenario.
   Run the scenario through that analyzer.
   Generate its report.
   Publish its output.
   Keep all these actions within the same session.
4. Explain these points:
   - What the feature does.
   - Why the scenario exposes the feature.
   - What each generated result means.
   - What the evidence cannot establish.
   - Which diagnostic first helps explain a failure.
5. Validate:

```sh
python3 .agents/skills/inet-80211-walkthrough-writer/scripts/validate_walkthrough.py \
  --require-analysis-visuals path/to/walkthrough.md
```

Use `PASS`, `FAIL`, `INCONCLUSIVE`, and `NOT RUN` exactly as defined in the contract.
Treat configuration as requested behavior.
Treat absent fields as unknown.
Throughput and frame counts alone do not establish the mechanism.
Keep session, run/seed, time window, capture point, and limitation near each claim.

Use other repository skills for unresolved configuration, standards, simulation, regression, or debugging questions; they must not generate substitute walkthrough analysis content.
