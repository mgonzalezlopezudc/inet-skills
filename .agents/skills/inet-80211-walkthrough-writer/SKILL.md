---
name: inet-80211-walkthrough-writer
description: Create, revise, or review concise, evidence-backed INET IEEE 802.11 walkthroughs when the active checkout provides the shared analyzer and its README. Use for explaining a Wi-Fi feature from current configuration and script-generated scalar/vector and PCAP evidence, including plots, tables, packet statistics, and frame exchanges. Do not use to invent or restore an absent analyzer workflow.
---

# Write IEEE 802.11 walkthroughs

Use `doc/project/requirement/accepted-requirements.md` for project-level documentation and evidence
obligations. This skill owns only the IEEE 802.11 walkthrough contract and analyzer workflow.

Read [walkthrough-contract.md](references/walkthrough-contract.md) and [analysis-machinery.md](references/analysis-machinery.md). Start new documents from [walkthrough-template.md](assets/walkthrough-template.md).

## Capability and placement gate

Before drafting or changing a walkthrough:

1. Read the active checkout's `doc/project/design/repository-layout.md` and
   `doc/project/rule/documentation.md`.
2. Verify that both `examples/ieee80211/analysis/wifi_analysis.py` and
   `examples/ieee80211/analysis/README.md` are tracked in the active checkout.
3. Verify that the requested document location matches the canonical distinction among examples,
   showcases, and tutorials. A measured argument with prose and charts belongs in `showcases/`, not
   `examples/`, unless the active project documents explicitly say otherwise.

If either analyzer file is absent or the requested placement conflicts with the project documents,
stop and report that the checkout does not support this workflow. Do not reconstruct the analyzer
from Git history, ignored bytecode, generated artifacts, or skill text.

## Analysis boundary

Only `examples/ieee80211/analysis/wifi_analysis.py` and its suite-owned components may generate or publish:

- scalar/vector plots and tables;
- PCAP plots and statistics tables;
- frame-exchange timelines and tables.

Do not replace or supplement these with `opp_scavetool`, TShark, ad hoc code, manual calculations, or hand-written tables. Extend the shared analyzer when output is missing. Preserve script-owned marker blocks and ledger entries; prose may interpret generated data but must not duplicate it.

## Workflow

1. Identify the example, configurations, current walkthrough, and generated sessions.
2. State one learning question and a small set of testable claims.
3. Use the shared analyzer to inspect, run, report, and publish without mixing sessions.
4. Explain the feature, why the scenario exposes it, what each generated result means, the limits of the evidence, and the first useful diagnostic for failure.
5. Apply the canonical documentation rules where they govern, then remove speculation and
   unnecessary jargon unless requested.
6. Validate:

```sh
python3 .agents/skills/inet-80211-walkthrough-writer/scripts/validate_walkthrough.py \
  --require-analysis-visuals path/to/walkthrough.md
```

Use `PASS`, `FAIL`, `INCONCLUSIVE`, and `NOT RUN` exactly as defined in the contract. Treat configuration as requested behavior, absent fields as unknown, and throughput/frame counts as insufficient for mechanism. Keep session, run/seed, time window, capture point, and limitation near each claim.

Use other repository skills for unresolved configuration, standards, simulation, regression, or debugging questions; they must not generate substitute walkthrough analysis content.
