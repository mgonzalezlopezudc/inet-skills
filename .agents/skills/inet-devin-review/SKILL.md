---
name: inet-devin-review
description: Read and summarize findings directly in Devin Review for a GitHub pull request. Use with a PR URL, an owner/repo#number reference, or a Devin Review link when the user asks what Devin found or what remains open, including without an API key.
---

# Read Devin Review findings

## Open the existing review

Use the supplied Devin Review link when available. For a GitHub.com PR link or an `OWNER/REPO#NUMBER` reference, open `https://app.devin.ai/review/OWNER/REPO/pull/NUMBER`. Keep the lookup read-only.

Open the review in a JavaScript-capable browser and wait for the PR title and findings controls to render. Use a signed-out browser for a public PR and an existing authorized Devin session for a private PR. If a plain web fetch returns only the application shell, use browser automation or an installed headless browser. If the page says the review is unavailable or the findings are inaccessible, report the displayed state and access gap. [Opening a Devin review](https://docs.devin.ai/work-with-devin/devin-review#other-ways-to-open-a-review)

With headless Firefox and geckodriver, Python's `urllib.request` can use the local WebDriver HTTP interface if a browser automation package is unavailable. Start `geckodriver --host 127.0.0.1 --port 0`, read the assigned address from its startup output, and create a headless Firefox session with `POST /session`. Close the session with `DELETE /session/<id>` and stop the driver after the lookup.

## Read findings in Devin

Use the **Bugs** view or the sidebar to inspect findings. In the **Info** sidebar, expand the **Bugs**, **Flags**, or **Vulnerabilities** groups as relevant. A group with a count of zero can still contain resolved findings. Expand each relevant finding to read its reasoning and any resolution note. [Reading a review](https://docs.devin.ai/work-with-devin/devin-review#reading-a-review) · [Finding statuses](https://docs.devin.ai/work-with-devin/devin-review#resolving-findings)

Check Devin's review history or stale-review banner for the reviewed commit. When assessing whether a finding still applies, compare the reviewed commit with the current PR head and check the relevant diff. [Review history](https://docs.devin.ai/work-with-devin/devin-review#navigate-changes-and-review-history)

## Report what Devin found

Lead with the open findings and summarize resolved findings when relevant. Give each finding's title, status, concern, and any available file, line, and resolution note. Link to the finding in Devin Review if available, or to the review page. If the review is behind the PR head, say which revision Devin reviewed when known. If the current diff already addresses a finding that Devin lists as open, cite the relevant change and report Devin's displayed status.
