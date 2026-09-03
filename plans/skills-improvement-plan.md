The report supports a six-milestone program. Start with measurement and routing fixes; defer new specialist domains until usage data justifies them.

Important repository detail: the authoritative skill files are tracked in `/home/user/omnetpp_ws/inet-skills`. The `.agents/` directory in this checkout is an exact but Git-excluded copy, so implementation should happen in `inet-skills` and then be deployed here.

## Actionable plan

| Order | Milestone | Deliverables | Completion criteria |
|---:|---|---|---|
| 1 | Evaluation foundation | Suite manifest, static linter, behavioral fixtures, baseline report | Every skill has positive/negative activation cases; links, dependencies, metadata, commands, and packaged files are validated |
| 2 | Routing and context reduction | Narrow orchestration, add mechanical middle path, tier authoring context | Ordinary tasks stop over-triggering orchestration; semantic changes retain existing safety gates |
| 3 | Generic regression support | Add `inet-regression-testing`; slim the Wi-Fi specialization | Protocol-neutral regression requests route correctly; WLAN-specific obligations remain intact |
| 4 | Structured verification results | JSON schema and adapters for unit/module, fingerprint, and `opp_repl` | Supported runners produce consistent, validated envelopes without interpreting correctness |
| 5 | Maintenance cleanup | Generated metadata, packaging hygiene, orphan cleanup, walkthrough profile | Duplicate hand-maintained files and stale deployment artifacts are eliminated |
| 6 | History and performance decision gates | Evaluate `inet-opp-repl` and performance skill demand | Add either capability only when task frequency and maintenance ownership justify it |

### 1. Build the evaluation foundation first

Create in the `inet-skills` repository:

- `.agents/skill-suite.yaml`
  - Skill dependencies.
  - Required tools and checkout files.
  - Deployment profiles: `core`, `wifi`, `results`, `history`, `walkthrough`.
  - Canonical metadata used to generate platform YAML.
  - Compatible `doc/project/` revision or capability checks.
- `scripts/validate_skill_suite.py`
  - Validate frontmatter and metadata consistency.
  - Detect broken and orphaned references.
  - Verify declared dependencies and required files.
  - Reject `*.pyc` and `__pycache__` in deployment artifacts.
  - Check generated metadata with a `--check` mode.
- `tests/skill-suite/`
  - At least one positive and one negative activation case for each of the 23 skills.
  - Representative end-to-end cases for authoring, review, debugging, results, regression, branch cleanup, and rebase.
  - Assertions on required workflow gates rather than exact generated wording.
- A baseline report recording activation accuracy, workflow correctness, unnecessary skill loads, turns, tokens, runtime, and unsupported capabilities.

Do not modify routing before this baseline exists. Subsequent milestones should rerun the same corpus and report before/after results.

### 2. Reduce routing and context overhead

Update [inet-agent-orchestration](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-agent-orchestration/SKILL.md):

- Narrow its description to tasks that genuinely require delegation, independent evidence lanes, or specialist handoffs.
- Replace Chimp/Dog/Fish/Ant with semantic names such as `reasoning`, `navigation`, `implementation`, and `extraction`.
- Keep three execution paths:
  1. trivial localized change;
  2. wide but behavior-preserving mechanical change;
  3. semantic change requiring the full contract pipeline.
- Define the mechanical path by invariant—repetitive, behavior-preserving, independently checkable—not only line count.
- Retain sealing, focused verification, approval, and independent-review gates for semantic work.

Update [inet-code-authoring](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-code-authoring/SKILL.md):

- Add small, medium, and large context tiers.
- Load only the primary preventive reference for a small focused change.
- Load cross-layer references when the runtime contract actually crosses layers.
- Declare its dependency on code-review-owned references in the manifest.
- Add a selectively loaded reference for broad renames, migrations, and generated-artifact updates.

Also expand [inet-unit-tests](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-unit-tests/SKILL.md) discovery text to explicitly include module tests.

Acceptance tests should demonstrate:

- A normal single-agent production change does not activate orchestration merely because it is nontrivial.
- A multi-lane diagnosis still activates orchestration.
- A wide rename selects the mechanical path.
- A behavioral change cannot incorrectly enter either fast path.
- Existing seal and pre-write-contract obligations remain enforced.

### 3. Add protocol-neutral regression design

Create `.agents/skills/inet-regression-testing/` with this responsibility:

> behavior claim → invariant → matching test category → minimal deterministic reproduction → direct evidence → bounded seed/parameter campaign

It should:

- Route test-category policy to [testing.md](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/rule/testing.md) and [test-anatomy.md](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/design/test-anatomy.md).
- Distinguish helper coverage from production-path evidence.
- Define when one seed is enough and when a campaign is warranted.
- Route execution to existing unit, module, simulation, fingerprint, result, and debugging skills.
- Remain protocol-neutral.

Then reduce [inet-80211-regression-testing](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-80211-regression-testing/SKILL.md) to Wi-Fi-specific invariants, standards obligations, HE/EHT feature gates, and packet-exchange evidence. Declare the generic skill as its dependency.

### 4. Normalize verification output

Introduce a versioned JSON schema containing:

- Command and working directory.
- Build mode.
- Runner and selector/filter.
- Configuration, run, and seed where applicable.
- Number of cases executed.
- `PASS`, `FAIL`, `ERROR`, `INCONCLUSIVE`, or `NOT_RUN`.
- First causal failure available from the runner.
- Artifact paths.
- Flaky status.
- Whether a changed result was expected and approved.

Implement adapters incrementally:

1. Unit and module runners.
2. Fingerprint runner.
3. `opp_repl`.

Add fixtures covering pass, assertion failure, runner/build error, zero-test selection, malformed output, and expected baseline change. Keep causal interpretation in the owning skill; the adapter should normalize facts only.

### 5. Remove concrete maintenance debt

- Retire [high-value-flag-checks.md](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-code-review/references/high-value-flag-checks.md) after confirming its unique checks are either already represented or deliberately migrated. It currently has no inbound Markdown reference.
- Generate each skill’s `openai.yaml` and `antigravity.yaml` from shared metadata. The corresponding files are currently byte-for-byte identical for every skill.
- Add generation drift checks to the suite linter.
- Exclude `__pycache__` and `*.pyc` from deployment. The observed files are already ignored rather than tracked, so this is primarily a packaging fix.
- Exclude `inet-80211-walkthrough-writer` from the default deployment profile unless both analyzer files exist. They are absent in this checkout, and the skill already has the correct runtime stop condition.
- Keep the small evidence-specific diagnostic skills separate.

### 6. Use explicit decision gates for optional work

For the branch workflows:

- Measure how often cleanup and high-risk rebase are actually invoked.
- If both remain supported workflows, create `inet-opp-repl` to own command discovery, dependency mapping, result semantics, and the shared verification envelope.
- Move detailed recovery and per-stage rebase mechanics out of the top-level [rebase skill](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-branch-rebase/SKILL.md) into selectively loaded references.
- Keep cleanup and rebase as distinct entrypoints because their authorization and history guarantees differ.

For performance:

- Record real performance/scalability requests for an agreed observation period.
- Add `inet-performance-analysis` only if recurring demand appears.
- Its initial scope should cover repeatability, warm-up, wall-clock and memory measurement, profiler evidence, before/after comparison, and `tests/speed` integration.

## Recommended commit series

1. `skills: add suite manifest and validation harness`
2. `skills: add activation and end-to-end evaluation corpus`
3. `skills: narrow orchestration and tier authoring context`
4. `skills: add protocol-neutral regression testing`
5. `skills: normalize verification result envelopes`
6. `skills: generate platform metadata and clean deployment artifacts`
7. Optional: `skills: centralize opp_repl workflow mechanics`

Each commit should leave the static validator green. Behavioral changes should include their corresponding activation fixtures in the same commit.

No files were modified while producing this plan.