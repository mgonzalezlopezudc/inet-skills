# Independent project guidance and skill evaluation — 2026-09-06

## Scope and controls

Skill source: this repository. Project checkout: `/home/user/omnetpp_ws/inet`. Its `.agents` copy
was not edited or refreshed. Baseline source revision: `3555facd73e74d941ee3e2a3d0a79f99f3904ed2`.

The evaluation fixtures, semantic grading rubric, raw answers, and isolated trial patches are in
[../evaluations/](../evaluations/README.md). Snapshot file digests identify the evaluated revised
text. All evaluators used GPT-6 Astra, medium reasoning, the same six tasks and project fixture,
and read-only inspection. They did not receive the grading rubric or other variants' answers.
The fixture moves policy behind the contributor map and changes verification to a release wrapper.
These are synthetic decision checks, not INET runtime tests.

## Six-case smoke comparison

Root manually checked each answer against the saved rubric. All variants correctly resolved INI
precedence, rejected stale-library and zero-selection evidence, proposed correct refusal ownership
handling with direct tests, withheld unexplained baseline acceptance, and accepted the valid
run-level aggregation without inventing a defect.

| Variant | Correct cases | Unsupported findings | Questions | Seconds | Files read |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 6/6 | 0 | 0 | 72.2 | 28 |
| Revised discovery | 6/6 | 0 | 0 | 92.9 | 29 |
| Revised + compact contract trial | 6/6 | 0 | 0 | 72.0 | 29 |

Actual token/context accounting was unavailable. File counts are not token measurements. One run
per variant cannot establish a speed or accuracy improvement; service/tool timing varies. In
particular, the baseline already followed the changed policy correctly. The independence change
removes static coupling; this experiment does not demonstrate an accuracy gain.

## Adoption decisions

Retain the full authoring contract for now. The compact prototype preserved correctness on one
simple ownership case, but lacks coverage of the more complex boundaries whose protection justified
the full form. The patch is retained for further controlled evaluation, not installed in the suite.

Keep default profile and specialized entry-point behavior unchanged until their routing benefit is
established. A smaller existing profile can be selected explicitly; reducing its advertised skills
alone does not demonstrate better task outcomes.

## History routing

Two additional cases cover exact-authorized same-base reconstruction and a rebase with unresolved
ownership-contract overlap. The correct choices are straightforward cleanup (after admission
checks, without renewed approval for identical specified boundaries) and full rebase with a concrete
ownership adaptation and evidence before a safe-point claim. No history mutation was performed.

| Variant | Correct routing | Questions | Seconds | Files read |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 2/2 | 0 | 57.5 | 11 |
| Revised discovery | 2/2 | 0 | 76.7 | 13 |
| Revised + consolidated entry-point trial | 2/2 | 0 | 97.1 | 17 |

The consolidated router retained the important admission distinctions but required more file reads
in this small comparison. It does not establish a benefit; retain the separate entry points and
keep the prototype patch for future evaluation. Timing is observational, not a reliable ranking.

## Smaller-profile trial

Isolated packaging of the existing core and default profiles succeeded (exit 0). Core contained
16 skills, default 26. Core omitted both result-analysis skills required by the six-case corpus;
default contained all named case skills. This is a deterministic availability observation, not an
agent activation benchmark. Retain the default; core remains available for explicitly narrower work.
No generated package was installed into the project checkout.

## Validation record

The implemented discovery and packaging revision is `f367cf9`; independent compatibility tests and
CI are in `5d9c706`. All 27 unit tests pass, and the suite validator reports 27 skills and zero
warnings. Isolated core, Wi-Fi, results, history, and default packages passed validation. Independent
review cleared the final changes after correcting a residual unconditional debug-mode instruction.
The missing verification fixtures noted in the initial project-copy assessment already existed in
this source repository, so no speculative restoration was needed.

The paired trials above used a frozen pre-final snapshot identified by `snapshot-sha256.json`.
After the final wording corrections, a fresh evaluator checked all eight cases against the exact
final skill snapshot, identified by `final-snapshot-sha256.json`. Its
[raw answers](../evaluations/answers/final.md) pass all eight rubric cases with zero unsupported
findings and zero questions. It read 42 unique files in 137 seconds; actual token usage remains
unavailable. This combined run is a final correctness smoke check, not a timing comparison with
the separate six-case and two-case trials. No proposed fix, build, or history operation in these
answers was actually executed.

The walkthrough's optional analyzer is absent from the active project checkout, so that capability
remains conditionally unavailable. GitHub workflow execution was not exercised locally. Package
outputs stayed outside the project checkout; deployment remains the user's later action.
