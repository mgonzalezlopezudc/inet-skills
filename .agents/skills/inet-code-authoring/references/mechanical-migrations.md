# Wide mechanical changes

Use this reference for a repetitive transformation that may span many files while preserving an
independently checkable behavioral invariant. Typical examples are broad symbol renames, manifest
or configuration-key migrations with unchanged values, and regeneration after a mechanical input
change.

Do not use it for an API contract change, a state or protocol transition, different effective NED
or INI selection, changed serialization, altered generated semantics, or any transformation whose
correctness requires a runtime-behavior judgment. Route those through the full semantic contract.

## Mechanical contract

Complete this before the first write:

```text
### Mechanical Change Contract
- Invariant: <observable behavior and values that remain unchanged>
- Source Set: <authoritative files/symbols selected by explicit search>
- Derived Set: <generated files, registries, docs, tests, and metadata that must follow>
- Transformation: <one deterministic old-to-new or format mapping>
- Exclusions / Collision Check: <same spellings or paths that must not change>
- Independent Checks: <absence/presence searches, generator drift check, focused build/test>
```

If the source set or exclusions cannot be bounded, stop and return to semantic discovery.

## Apply and verify

- Change authoritative inputs before derived artifacts. Regenerate outputs with the owning command;
  do not hand-edit generated files.
- Preserve spelling distinctions, namespaces, case, wire values, units, ordering, and configuration
  precedence unless the approved mapping explicitly includes them.
- Search the complete scoped tree for both old and new forms. Classify every remaining old form as
  intentional or missed; a zero-match assertion is valid only when the old form has no exclusions.
- Use an independent structural check appropriate to the invariant: generated-metadata drift,
  serializer round-trip, build graph, configuration dump, or an exact before/after inventory.
- Run `git diff --check`, inspect the whole diff for non-mechanical edits, and run focused tests for
  affected consumers. A green build alone does not prove behavior preservation.
- Treat any changed result, fingerprint, packet exchange, registration set, or effective
  configuration as evidence that the mechanical classification may be wrong. Do not update a
  baseline to preserve the classification.

Record the invariant, transformation counts, exclusions, exact commands, exit statuses, and any
unverified consumer in the implementation report.
