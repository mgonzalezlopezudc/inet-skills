# Working in the INET skill source repository

This file routes work; it does not copy project policy. The skill source is maintained separately
from an INET checkout and must remain usable without a local deployment of its skills.

When a skill task depends on INET project requirements, identify the active INET checkout from the
task context and read its stable `doc/project/README.md` entry point. Follow the routes exposed there
and use the current documents' paths, terms, commands, modes, approval requirements, and protection
status. If the entry point or required route is missing, report the gap and do not treat it as
permission. The packaged skills carry the discovery procedure in
`.agents/references/project-guidance-discovery.md`.

For changes to this repository, keep package integrity and skill behavior independently verifiable:

```sh
python3 scripts/validate_skill_suite.py --root . --check
python3 -m unittest discover -s tests/skill-suite -p 'test_*.py' -v
```

Validate an isolated profile in a directory outside the repository. The output directory must not
already exist:

```sh
package_parent="$(mktemp -d)"
python3 scripts/package_skill_suite.py --root . --profile results \
  --output "$package_parent/deployment"
python3 scripts/validate_skill_suite.py --root . --check \
  --deployment-root "$package_parent/deployment"
```

Use `apply_patch` for hand-authored file changes. Keep generated metadata synchronized through the
validator's supported option, and do not write package output into an active INET checkout or its
skill copy.
