# Baseline inventory before review

The inventory identifies selected baseline files and their historical source evidence. A recorded source origin is the INET revision used to produce a file. A comparison control is a source revision that this review tests against the file. These facts remain separate even when they name the same revision. SKILL.md defines the phase order and work limits.

## Select files for the requested area

Pin the source endpoint and both baseline repository revisions. Record local changes before file inspection. Read committed baseline content at those revisions when local files differ. Preserve local changes separately.

Use result metadata, effective configuration, model types, and source relationships to select relevant cases. A directory name alone does not establish protocol relevance. For IEEE 802.11, include MAC cases and PHY cases that use an 802.11 radio with a generic MAC. Include mixed-protocol cases when their results measure an 802.11 interaction. Record the selection evidence and exclusions.

Map statistical cases to their tracked scalar baseline files. Map chart analyses to their configured reference images through export filenames and repository links. Follow the active chart runner's scope. Do not include network diagrams or untracked comparison images as chart baselines. Record cases without a stored baseline separately.

## Find each file's baseline commit

Find the latest commit that changes each selected file at the pinned baseline revision. For example:

```sh
git -C "$baseline_repo" log -1 --format='%H%n%s%n%aI%n%cI' \
  "$baseline_revision" -- "$baseline_path"
git -C "$baseline_repo" rev-parse "$baseline_revision:$baseline_path"
```

The first command returns the commit ID, subject, author timestamp, and committer timestamp. The second command identifies the committed file content. Preserve full IDs in the machine-readable inventory. Record renames when they affect historical path lookup.

Keep statistics and media groups separate, even when their subjects describe the same source change. Group selected files by their latest baseline commit. Each group shows the commit ID, original subject, labeled author date, and complete file list. Retain every file exactly once in each repository's inventory. Expandable groups can keep a long appendix easy to read.

These groups describe the current selected files. They do not list every file that each historical commit changed. Git author dates describe authorship, not necessarily execution or publication time. Preserve committer timestamps for evidence recovery. Do not infer source order from either date.

## Recover historical source evidence

Read the baseline commit messages and relevant earlier history within the recovery limit. Check run metadata, CI records, saved logs, and existing provenance reports for source revisions. Classify each reference as a recorded source origin, a comparison control, or a suspected cause. A cause commit alone does not establish the origin.

For a documented origin, record the source ID, original subject, date, and evidence location. Otherwise, record the origin as unknown. State the scope that the evidence actually covers. A partial update at source X does not establish every baseline file at X. Attach evidence to individual files when one group contains different origins.

Show the origin or unknown beside each baseline group. Store control revisions, conditions, and outcomes separately when comparisons execute. A successful control must not change an unknown historical origin into a documented origin.

For example, suppose revisions A and B produce identical scalars. A comparison at B reproduces the file. That result does not identify which revision originally produced it. The origin remains unknown unless historical evidence identifies it.

Git ancestry supplies source order after the origins are documented. Author and committer dates cannot establish order across the statistics and media repositories. Record incomparable branches or missing history without an assumed linear order.

Never convert a baseline repository SHA into an INET source SHA by assumption. Never treat the latest successful suite run as the endpoint for older files without evidence.

## Keep controls from different source revisions separate

For example, suppose case X records its baseline at source A and case Y records its baseline at later source C. Start at A. Review X forward from A. Introduce Y's baseline at C, unless an earlier historical baseline for Y has a valid source control. This prevents Y's newer expectations from becoming a false failure at A.

