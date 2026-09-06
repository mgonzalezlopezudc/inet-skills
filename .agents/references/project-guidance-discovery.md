# Discover active project guidance

The skill suite has one project documentation input: the active checkout's
`doc/project/README.md`. The files and names linked from that entry point are
project-owned details and may move, be renamed, or be reorganized without a
skill update.

Before applying project policy:

1. Identify the active checkout from the task context. When the location is
   unclear, run `git rev-parse --show-toplevel` in the intended working
   directory and verify the result.
2. Read `<checkout>/doc/project/README.md`. Do not use a copy shipped with the
   skills, a remembered path, or a hardcoded rule identifier.
3. Follow the entry point's route that matches the task. If it does not expose
   a route, search the current `doc/project/` tree for the task terms and
   report the search used. Treat the linked documents and their current text
   as authoritative.
4. Extract the obligations needed for this task: ownership and protection,
   acceptance criteria, build modes, executable gates, test category and
   filter, approvals, and reporting fields. Record the source paths discovered
   and the exact commands selected from current guidance.
5. Refresh the discovery after changing checkout, branch, or project
   documentation. A changed command, mode, or policy takes effect on the next
   discovery.

Missing guidance has no permissive meaning. If the entry point or guidance
needed for a protected or otherwise required action is absent, stop that
action and report the missing route. If optional domain guidance is absent,
record the capability gap and continue only with work whose requirements are
already established. Do not reconstruct policy from skill text or silently
substitute a similarly named document or executable.

This procedure preserves technical task knowledge in the skills while leaving
project requirements, identifiers, headings, gates, and protection decisions
in the active checkout.
