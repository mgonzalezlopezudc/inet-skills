# Skill decision evaluations

These six small, synthetic cases measure decisions from supplied evidence. They do not execute
INET or establish simulator correctness. The project fixture deliberately relocates internal
guidance and requires release-mode verification through a wrapper.

Materialize a fresh fixture outside any deployment tree:

```sh
python3 tests/skill-suite/evaluations/prepare.py /tmp/inet-decision-evaluation
```

Give an independent evaluator only that fixture and one pinned skill snapshot. Ask it to read each
TASK.md, apply the named skills, follow project guidance from doc/project/README.md, and return
answers without executing proposed builds or modifying source. Do not expose rubric.json, other
variants' answers, or the suspected defects. Keep model, reasoning effort, task order, tools and
project fixture identical across variants. Record skill revision or snapshot digest, answers,
elapsed wall time, files read, questions and actual token usage when available.

Grade each case against rubric.json manually, based on semantic correctness rather than phrase
matching. Record unsupported findings separately, especially on the clean aggregation case.
Proposed verification must never be graded as executed evidence. Package validation and agent
behavior are separate results.

A single run per variant is a bounded smoke comparison, not a statistically reliable speed or
accuracy estimate. Timing includes tool and service variation; file counts do not measure tokens.
Do not adopt a workflow simplification merely because one run was faster. Extend the cases and
repeat with controlled order when an adoption decision needs stronger evidence.
