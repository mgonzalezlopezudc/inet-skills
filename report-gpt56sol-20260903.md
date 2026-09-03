The skill set is strong and unusually disciplined, but somewhat over-engineered at the orchestration layer. I would keep all major capabilities, reduce default activation and maintenance overhead, and add empirical evaluation plus generic regression support.

Scope: the 23 repository-owned skills under `.agents/skills`. Ratings are design-based; there is no visible suite-level evaluation or usage telemetry.

| Dimension | Assessment | Why |
|---|---:|---|
| Effectiveness | 8.5/10 | Excellent evidence discipline, safety gates, and task-specific procedures |
| Efficiency | 7/10 | Good progressive disclosure, offset by broad orchestration triggers and heavy workflows |
| Utility | 8.5/10 | Excellent for INET and especially IEEE 802.11; weaker for generic regression design |

The inventory contains 1,481 top-level lines / 12,666 words, plus 34 references and four source scripts. All 42 local Markdown links resolve.

### What works especially well

- Canonical policy remains in `doc/project/`; skills mostly add mechanics and routing instead of copying rules. This matches the repository’s “cite, do not repeat” principle at [README.md:147](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/README.md:147) and is particularly explicit in [inet-architectural-requirements:8](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-architectural-requirements/SKILL.md:8).
- The authoring contract forces ownership, control paths, sibling behavior, boundaries, and verification to be understood before editing. Its validation gate is excellent: [inet-code-authoring:65](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-code-authoring/SKILL.md:65).
- Review is both independent and evidence-oriented. Its context-budget tiers are a very good pattern: [inet-code-review:58](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-code-review/SKILL.md:58).
- The small diagnostic skills preserve important evidence boundaries: configuration, logs, event logs, captures, packet tags, LLDB, results, and fingerprints are not treated as interchangeable.
- Failure handling is unusually mature: zero-test runs are rejected, missing canonical gates stop explicitly, and unsupported walkthrough environments do not trigger improvised replacements.
- The Wi-Fi suite is excellent: it separates normative standards, implementation, runtime evidence, and inference.

### Main weaknesses

1. Orchestration activates too broadly. Its description covers almost every substantial INET activity [at line 3](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-agent-orchestration/SKILL.md:3), even though orchestration adds value primarily when delegation or independent evidence lanes exist.

2. The fast track is too binary. The ≤5-line threshold [at line 56](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-agent-orchestration/SKILL.md:56) leaves no middle path for larger but purely mechanical changes.

3. Generic regression design is missing. The WLAN regression skill provides claim → invariant → deterministic scenario → evidence reasoning [at line 8](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-80211-regression-testing/SKILL.md:8), while the generic test skill mostly provides runner mechanics.

4. Authoring lacks the context-budget tiers already present in review. It requires the common pitfalls and every selected layer reference for every semantic change [at line 17](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-code-authoring/SKILL.md:17).

5. Some dependencies are implicit. For example, authoring directly consumes references owned by code review. That is sensible reuse, but independent installation or partial deployment would be fragile.

6. Rare workflows are large. Branch rebase is 227 top-level lines, while branch cleanup is 132; their state and `opp_repl` contracts partly overlap. Their rigor is valuable, but they are likely bit-rot candidates unless exercised regularly.

7. Verification results have no common machine-readable envelope. Individual skills explain how to classify failures—for example, unit tests distinguish library, executable, and assertion failures [at line 40](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-unit-tests/SKILL.md:40)—but the orchestrator must still interpret heterogeneous raw build, test, fingerprint, simulation, and CI output.

8. Performance and scalability are uncovered specialist domains. The project explicitly recognizes `speed` as a distinct test category [at line 26](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/design/test-anatomy.md:26), yet no skill owns performance measurement, profiling, memory growth, or performance-regression comparison.

### SWOT

| | Positive | Negative |
|---|---|---|
| Internal | **Strengths:** canonical ownership, strong evidence boundaries, precise commands, safe escalation, progressive disclosure, explicit deliverables | **Weaknesses:** orchestration overhead, uneven context budgeting, implicit dependencies, WLAN-centric regression guidance |
| External | **Opportunities:** empirical skill evals, deployment profiles, generic regression support, structured verification results, performance analysis, generated metadata, centralized `opp_repl` mechanics | **Threats:** drifting rule identifiers/tool paths, co-triggered skills consuming context, platform-binding drift, rare workflows becoming stale |

### What I would add

1. **A skill evaluation and lint harness — highest priority.**  
   Test positive and negative triggers, required workflow steps, broken/orphan references, unavailable commands, dependency declarations, compatibility with the active `doc/project/` revision, and frontmatter/body mismatches. Add representative end-to-end tasks and measure correctness, turns, tokens, runtime, and unnecessary skill activation. Without this, “effectiveness” remains inferred.

2. **`inet-regression-testing`.**  
   Make it protocol-neutral: behavior claim → invariant → test category → minimal deterministic reproduction → seed/parameter campaign → direct evidence. Then make `inet-80211-regression-testing` a thin WLAN specialization or reference.

3. **A non-triggering capability/dependency manifest.**  
   Map change type and path glob → primary skill → supporting skills → specialist agent → required files/tools → compatible project revision. Also define deployment profiles such as `core`, `wifi`, `results`, `history`, and `walkthrough`. Generate runtime-specific metadata from this manifest where possible.

4. **A structured verification-result adapter.**  
   Normalize stable runner output into a small JSON envelope containing command, working directory, mode, selector, cases run, status, first failure, artifact paths, and whether the result was flaky or expected to change. Start with unit/module, fingerprint, and `opp_repl`; let the same adapter ingest CI logs when available. Keep causal interpretation with the responsible skill rather than encoding it in the parser.

5. **`inet-opp-repl`, if branch reconstruction remains important.**  
   Centralize command discovery, dependency mapping, result semantics, and common evidence fields now distributed between cleanup and rebase.

6. **Authoring context tiers and a wide-mechanical-change path.**  
   Mirror the small/medium/large structure from code review so low-risk changes do not load every preventive reference. Add a selectively loaded migration/refactoring playbook for broad renames, API migrations, and generated-artifact updates; this fills the current gap between the ≤5-line fast track and the full semantic-change pipeline without creating another top-level skill.

7. **Performance/scalability support, if speed work is recurring.**  
   Add `inet-performance-analysis` or a reference owned by generic regression testing for reproducible wall-clock and memory measurements, profiler use, warm-up and repetition policy, before/after comparison, and `tests/speed` integration. Establish demand with actual performance tasks before making it part of the default profile.

### What I would remove or streamline

- Retire or explicitly route [high-value-flag-checks.md](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-code-review/references/high-value-flag-checks.md:1). It is 253 lines / 2,573 words with no inbound reference and overlaps the routed review catalogs.
- Remove generated `.pyc` files from deployment. Four bytecode files contribute about 88 KB, including stale architecture-script bytecode without corresponding source in that skill.
- Keep `inet-80211-walkthrough-writer`, but remove it from the default profile when the shared analyzer is absent. The current checkout lacks both required analyzer files, so the skill must stop under its own capability gate [at line 15](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-80211-walkthrough-writer/SKILL.md:15).
- Generate the 23 identical OpenAI/Antigravity metadata pairs from one source rather than maintaining 46 hand-editable YAML files.
- Expand the `inet-unit-tests` trigger to say “unit and module tests”; module-test execution currently exists only in the body [at line 31](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-unit-tests/SKILL.md:31).
- Move detailed rebase recovery mechanics into selectively loaded references, while keeping the top-level `inet-branch-rebase` identity and safety gate.
- Replace the Chimp/Dog/Fish/Ant labels with semantic names such as `reasoning`, `navigation`, `execution`, and `extraction`. The animal taxonomy [at line 36](/home/user/omnetpp_ws/inet-pr-doc-project/.agents/skills/inet-agent-orchestration/SKILL.md:36) adds decoding cost without improving routing.

I would not merge the small configuration/log/eventlog/PCAP/result/debugger skills. Their apparent overlap is useful separation by evidence type and side effect. The right reduction target is activation and maintenance overhead, not capability granularity.
