---
name: inet-devin-review
description: Retrieve and summarize existing Devin Review findings for a GitHub pull request. Use for a GitHub PR or Devin Review link when the user asks what Devin flagged, which findings remain open, or how to read them without an API key.
---

# Read Devin Review findings

Identify the repository and PR number from the supplied GitHub or Devin Review link. For GitHub.com PRs, the Devin Review URL is `https://app.devin.ai/review/OWNER/REPO/pull/NUMBER`. Keep the lookup read-only and use the existing review.

## Read GitHub's posted findings

Use the GitHub connector when available. For an anonymous lookup on a public PR, use the GitHub web page or these REST routes under `https://api.github.com/repos/OWNER/REPO`, following pagination as needed.

| Route | Contents |
| --- | --- |
| `GET /issues/NUMBER/comments` | Conversation comments and links to the review |
| `GET /pulls/NUMBER/reviews` | Review summaries and their commit SHAs |
| `GET /pulls/NUMBER/comments` | Inline findings with file and line information |

Filter for the Devin bot, typically `devin-ai-integration[bot]`. GitHub posting settings can leave only a count and a link. Use the Devin Review page to retrieve the details in that case or whenever the user asks for all findings. [GitHub comments](https://docs.github.com/en/rest/issues/comments#list-issue-comments) · [GitHub reviews](https://docs.github.com/en/rest/pulls/reviews#list-reviews-for-a-pull-request) · [GitHub inline comments](https://docs.github.com/en/rest/pulls/comments#list-review-comments-on-a-pull-request) · [Devin posting settings](https://docs.devin.ai/work-with-devin/devin-review#posting-to-github)

## Read findings in Devin

Open the supplied or derived URL in a JavaScript-capable browser. Try a signed-out browser for public PRs. If a web fetch returns an empty application shell or cannot open the page, use browser automation or an installed headless browser such as Firefox with geckodriver. Wait until the PR title and findings controls render.

If Python browser packages are unavailable, geckodriver's local WebDriver HTTP interface works with Python's `urllib.request`. Launch `geckodriver --host 127.0.0.1 --port 0`, read the assigned address from its startup output, and use `POST /session` with headless Firefox. Preserve the page result, then close the session with `DELETE /session/<id>` and stop the driver. If the Firefox Snap driver's PID is still live and host-shell termination fails with `PermissionError`, use `snap run --shell firefox.geckodriver -c "kill -KILL $driver_pid"` only for the verified PID of the driver started for this lookup.

Open the **Flags**, **Bugs**, and **Vulnerabilities** groups in the analysis sidebar or the findings view that the page provides. Expand finding titles to read their reasoning and any resolution note. Check for resolved entries even when the badge counts only open findings. Use navigation and detail controls to inspect the existing review.

For a private PR, use an existing authorized GitHub connection for posted comments or a signed-in Devin session with repository access for the review page. If the finding details are inaccessible, report the visible evidence and the access gap. The Devin v3 review endpoint provides status and commit metadata. [Devin Review](https://docs.devin.ai/work-with-devin/devin-review#reading-a-review) · [Devin status response](https://docs.devin.ai/api-reference/v3/pr-reviews/get-organizations-pr-reviews)

## Report what Devin found

Lead with the open findings and summarize resolved findings when relevant. Give each finding's title, file and line if available, concern, and resolution note. Link to the Devin Review or specific GitHub comment. If the GitHub summary and Devin page differ, report the counts with their sources and check the reviewed commit against the current PR head before attributing the difference to an older revision. If the current diff already addresses an open finding, cite the relevant change and distinguish that observation from Devin's displayed status.
