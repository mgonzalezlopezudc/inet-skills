# Workflow

Build requirements now use `MODE=sanitize` and `make -j8`; the required gate
is `tools/check-current-policy`. These names intentionally differ from the
historical project commands.
