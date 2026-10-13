# English walkthrough: recording notes

Target length: 4–5 minutes. These are rehearsal prompts, not a script to read verbatim. Record the candidate's own English explanation and a real Dify run. A local Python smoke test is not a substitute for the complete Workflow execution required by the assessment.

## Before recording

Install the package, import the workflow, select the provider credential profile, and verify a successful run. Close credential settings and unrelated tabs. Use a public issue. Increase browser zoom enough to make inputs and node results readable. Disable private notifications.

## 0:00–0:35 — The user problem

Show the README and the Dify canvas.

Explain: a maintainer receives a report without enough context. The goal is to make the first investigation useful, without guessing the cause or promising a fix.

Points to cover in your own words:

- The input is one public repository and issue number.
- The output is an investigation brief and a reply draft.
- Nothing is posted back to GitHub automatically.

## 0:35–1:20 — Plugin and external API

Open `plugin/github_client.py` and the two tool files.

Explain:

- The SDK adapters emit explicit variables: `status` and `payload_json`.
- The client calls GitHub's repository, issue, comment and search REST endpoints.
- The API host is fixed; tokens are optional and sent only in the authorization header.
- A private repository is rejected before retrieving its issue body.
- Requests have timeouts; 401, 403, 404, rate limits and network failures have different messages.

Do not open a real token. You can show the YAML `secret-input` declaration instead.

## 1:20–2:05 — Why this is a workflow

Show the actual canvas and trace the branches.

- First tool: retrieve context.
- Code: inspect failure/security signals and missing information.
- Conditional: stop for an API error or potential security report.
- Second tool: search related issues for normal reports.
- Code: combine facts, limitations, next checks and a draft reply.

Explain the trade-off: explicit rules make the demo reproducible and avoid a paid model dependency, but they cannot understand every report. Similar titles are candidates, not confirmed duplicates.

## 2:05–3:35 — Required complete execution

Keep the screen recording running from input to final output.

1. Enter `langgenius/dify` and `36283` (or another verified public issue).
2. Click Run and wait for completion.
3. Show the overall success state and the real node trace.
4. Open the first tool's output, then the conditional branch and related-search output.
5. Read the final report briefly. Point to the original source, investigation order, and the review-before-posting wording.
6. If a live API fails, show the real error and explain it; do not replace it with a fabricated successful trace. Retry only when appropriate.

## 3:35–4:15 — One failure path

Run `repository: not a repo` with issue number `1`. Show the actionable error result. Explain that an invalid input does not produce a fake diagnosis and should not cause an external request.

## 4:15–4:50 — Limits and handoff

Explain the five-comment cap, partial-search behavior, keyword limitations, and the fact that Dify execution logs can contain issue data even when the final security report omits it. Show the GitHub repository, installable package and the DSL exported from the successful Dify app.

Finish with what you would improve next: better multilingual context checks and a small evaluation set of real, sanitized reports, before adding automated actions.

## Questions to be ready for

- Why use a plugin instead of putting every request in HTTP nodes?
- Why emit `payload_json` explicitly instead of relying on generic tool JSON output?
- What distinguishes a GitHub 403 permission error from a rate-limit response?
- Why can an API call and a UI run differ even with the same visible input?
- What happens if comments or related search fail?
- What can the security branch prevent, and what can still remain in logs?
- Where does your implementation stop being reliable?

## Publishing the video

Upload the real recording to a service that supports link viewing. Check it in a signed-out browser, verify playback and audio, and use the final video URL in the submission. No candidate recording or video URL has been created yet.
