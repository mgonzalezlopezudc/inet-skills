# Discover active project guidance

The active checkout's `doc/project/README.md` is the skill suite's only fixed path for project guidance.
The project map owns the routes to task procedures and policy documents.
Read their contents for each task; the map alone does not establish their requirements.
Internal paths, identifiers, commands, and procedures can change without a skill update.

For example, a hypothetical project map links to a draft approval procedure.
The draft applies only after maintainer acceptance, which the current task does not establish.
The link alone does not activate that approval procedure.
The agent checks the document's status and task instructions before it selects the applicable requirements.

Before applying project policy:

1. Identify the active INET checkout from the task context.
   The skill source repository and a deployment directory are not INET checkouts.
   Use `git rev-parse --show-toplevel` in the intended directory if its location is unclear.
2. Read `<checkout>/doc/project/README.md`.
   Do not use a packaged copy, a remembered internal path, or a fixed rule identifier.
3. Select the route for the requested task.
   Resolve relative links from the document that contains each link.
   Read the selected procedure and the relevant sections of its linked policy, design, and enforcement documents.
   Follow further dependencies when they define a condition that affects the task.
4. Check each selected document's status, scope, and protection information.
   Use its current text to determine whether its requirements apply.
   A link does not make a draft accepted policy.
   Read the draft's conditions for use and the task instructions before you apply its approval process.
   Follow the named replacement for a superseded document.
   Use a snapshot as historical evidence, not as current policy.
5. Record the applicable obligations and their source paths.
   Include ownership, protection, acceptance criteria, commands, modes, selectors, approvals, and report fields where the task requires them.
   Confirm the selected executable and its supported options in the active checkout before execution.
6. Refresh this discovery when the checkout, branch, or relevant project documents change.
   Include relevant local edits; a commit identifier alone does not describe changed guidance.
   Recheck affected decisions and evidence against the new text.

## Select the task route

Use the current map's links, not this table, to choose document paths.
The table supplies search terms when a route is unclear.

| Task | Guidance to find |
| --- | --- |
| Prepare or review an implementation plan | Plan procedure, status conditions, technical design, verification, approval scope, and revision rules |
| Implement a change or add a protocol | Contribution procedure, requirements, ownership, reuse, protection, and applicable domain rules |
| Review code or a pull request | Correctness procedure, series rules, classification, exception ledgers, checklists, and report format |
| Audit or seal a subsystem | Audit procedure, protection scope, exception disposition, and permission requirements |
| Select or run tests | Test categories, claim coverage, freshness, focused gates, and publication gates when applicable |
| Derive tests from a standard | Standard evidence, protocol features, model coverage, failure classes, and expected outcomes |
| Diagnose a simulation | Reproduction, observation boundaries, evidence classes, controls, and diagnostic report |
| Compare or plot results | Measurement definition, independent repetitions, reductions, units, uncertainty, and report |
| Change a recorded expectation | Baseline scope, cause, correctness evidence, permission, and verification |
| Edit documents or describe a release | Audience, document owner, format, status, protection, compatibility, and release obligations |

## Handle an absent route

Search the current `doc/project/` tree for the task terms if the map lacks a clear route.
Report the search and the source that establishes applicability.
If a linked document is missing, report the broken route.
Use an explicit replacement only when current project guidance establishes it.

Missing guidance does not grant permission.
Stop an action if its required guidance is absent.
Continue independent work whose requirements are established.
Report absent optional domain guidance as a capability gap.
Do not reconstruct policy from skill text or substitute a document with a similar name.

## Use skill procedures with project policy

Skills supply tool procedures, discovery methods, and safeguards for their specific workflows.
Project documents supply project policy.
Adapt command examples to the discovered mode, scope, runner options, and acceptance criteria.
An example does not select debug mode or authorize a baseline update.
Use the current project format for a required report.
Retain the tool facts needed to reproduce the result.
Do not treat a skill template as an additional project report requirement.

Preserve the user's scope and existing authorization when you apply an approval procedure.
Request any required approval for a concrete result, after the work permitted before approval is complete.
Do not request the same approval again when it already covers the action.
