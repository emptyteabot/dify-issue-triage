# English walkthrough rehearsal script

This is a complete rehearsal script grounded in the installed plugin, exported Workflow and recorded Dify execution. Read the implementation first and explain it naturally in your own voice. AI coding assistance was used to develop the project.

The spoken text is approximately 419 words. At 100–120 words per minute, allow about 4–5 minutes including pauses. The existing silent template lasts about 2 minutes 48 seconds; its timestamps below identify the corresponding visuals, not a speaking deadline. Retiming the visuals to candidate-recorded audio is expected.

Record only the spoken paragraphs. Do not read section titles, visual directions or timing notes. One continuous voice recording with a short pause between sections is sufficient; separate clips are also fine. No face camera is required.

## 1. The problem

**Visual cue:** existing template 0:00–0:12. Project introduction.

Hi, this is my Dify assessment project, GitHub Issue Triage. It helps a maintainer review a public GitHub issue and prepare the next reply. The main goal is to collect evidence before deciding what caused the problem.

## 2. The plugin

**Visual cue:** existing template 0:12–0:33. Installed Dify plugin and its two tools.

The project has two tools built with the Dify Plugin SDK: Read public issue and Find related issues. They call the real GitHub API. A GitHub token is optional for public reads. When used, it stays in the provider's secret credential field.

## 3. API boundaries

**Visual cue:** existing template 0:33–0:58. Actual github_client.py source excerpts.

The client checks the repository format and issue number before making requests. It uses a fixed API host and request timeouts. It also checks that the repository is public before reading issue content. Authentication errors, rate limits, missing resources, and network failures have separate, useful messages.

## 4. Workflow routing

**Visual cue:** existing template 0:58–1:18. Explicit SDK output variables; describe the full Workflow routing.

Each tool returns status and payload_json as explicit variables. The workflow reads the issue, checks context, and chooses a branch. API failures and possible security reports go to a stop path. Ordinary issues continue to related search and report generation. If search fails, the main brief is still returned.

## 5. The real execution

**Visual cue:** existing template 1:18–1:26. Captured public Web App input, execution and result. These are real edited captures, not an uninterrupted realtime video.

Here is the published app running a real issue from the Dify repository, issue number thirty-six thousand two hundred and eighty-three. These captured screens show the input, execution, and final result.

## 6. The trace

**Visual cue:** existing template 1:26–1:43. Studio SUCCESS trace, seven nodes, 2.759 seconds and zero model tokens. The metric describes this one recorded run.

The Studio trace shows seven successful nodes, a runtime of about two point eight seconds, and zero model tokens. This version uses simple rules instead of an LLM. That makes its decisions easy to inspect, but limits language understanding.

## 7. Review the report

**Visual cue:** existing template 1:43–2:03. Source issue and investigation checklist. The source issue was already closed at recording time; this Workflow did not close it.

The report links to the original issue. In this example, connection refused selects a connectivity checklist. I would check the target service, host, port, and container network first. This is an investigation plan. The workflow has not confirmed the root cause.

## 8. Candidates and a draft

**Visual cue:** existing template 2:03–2:24. Related issue links and the draft reply.

Related issues come from title keyword search in the same repository. They are candidates for review, not confirmed duplicates. The suggested reply asks for useful evidence. It stays a draft: nothing is posted, labeled, or closed automatically.

## 9. Invalid input

**Visual cue:** existing template 2:24–2:28. Invalid-input result. Extend this visual when adding narration.

For an invalid repository, the workflow returns invalid_input and explains the required format. It stops without generating a diagnosis. This keeps bad input from becoming a misleading report.

## 10. Limits and handoff

**Visual cue:** existing template 2:28–2:48. Repository, exported DSL and published app handoff.

This version supports public repositories and reads at most five comments. Its English keyword rules can miss important context. Possible security reports skip search and omit issue text from the final brief, although earlier tool output can remain in execution logs. The repository includes the plugin package and the exported workflow YAML. The published app is also available. AI coding assistance was used; these checks and limits are documented.

## Implementation points to understand before recording

- The client uses GET requests only, a fixed api.github.com host, 5-second connection and 15-second per-request timeouts, and refuses redirects.
- Public visibility is checked before issue content is fetched. Anonymous reads work with lower rate limits; an optional token is sent in the authorization header.
- status and payload_json are explicit SDK variables. The JSON string is parsed by Workflow code instead of assuming the platform generic JSON-array shape.
- The normal path executes seven nodes; the graph contains eight because its two end nodes are mutually exclusive. Their output names are report and attention_report.
- If issue reading fails, stop. If selected comments fail, retain the issue and show a warning. If related search fails, retain the main brief and disclose the failure.
- Context checks detect signals rather than proving that information is complete or correct. Title search returns candidates, not semantic similarity or confirmed duplicates.
- Potential security reports skip search and omit issue text from the final brief. Earlier tool output can remain in execution logs.
- The project is rule-based, has no LLM dependency, and never posts replies or changes issue state.

## Before final submission

Replace the silent template video link with an accessible candidate-narrated video. Check that the final audio is intelligible, that the explanation matches the implementation, and that the complete real execution remains visible. Do not describe the silent template as the completed spoken-English demo.
