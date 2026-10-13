# Candidate English narration notes

The captioned template lasts about **2 minutes 48 seconds**. Aim for roughly 300–350 spoken words, and explain the implementation naturally in your own words. The notes below are prompts, not a transcript to read verbatim.

Record your own voice. No face camera is needed. Keep the recording free of private notifications and credentials. You can submit a separate voice recording for editing, or record your own full screen-and-voice walkthrough if you prefer.

## 0:00–0:12 — The problem

Explain who uses this: a maintainer handling an incomplete public GitHub report. The output is a context brief, related reports and a reply draft. It should help the first investigation without guessing a cause.

## 0:12–0:33 — The plugin

Name the two SDK tools: **Read public issue** and **Find related issues**. The real package is installed in Dify. Public access can use a blank-token credential profile; an optional GitHub token belongs in the provider's secret field, not Workflow inputs.

## 0:33–0:58 — The external API

Explain the fixed `api.github.com` host, repository/issue validation and request timeouts. Describe why 401, permission errors, rate limits, missing resources and network errors need different messages. The client rejects private repositories before reading their issue bodies and performs GET requests only.

## 0:58–1:18 — The Workflow

Explain the explicit `status` and `payload_json` tool variables. The Workflow reads context, inspects signals, branches for failures or potential security reports, calls related search for ordinary issues, and composes a report. It uses more than one tool call and has meaningful routing.

## 1:18–1:26 — The actual public run

The recording shows `langgenius/dify`, issue `36283`, being executed by the published Web App. Let viewers see the input, running step and final result. These are actual captures, edited for presentation.

## 1:26–1:43 — The trace

Point out the seven successful Studio nodes, 2.759-second runtime and zero model tokens. Explain the trade-off: explicit rules make the demo reproducible without an LLM credential, while limiting its language understanding.

## 1:43–2:03 — The report

Point to the original source and investigation order. A connectivity signal is not a confirmed diagnosis. Even when context signals are present, a person must verify the version values and reproduction.

## 2:03–2:24 — Related reports and reply

Related titles are keyword candidates, not proof of duplication. The draft asks for useful evidence and does not promise an unverified fix. Nothing is posted automatically; comments, labels and issue state remain under human control.

## 2:24–2:28 — The failure path

The invalid repository produces `invalid_input` and an actionable explanation. The stop result explicitly says no diagnosis was generated.

## 2:28–2:48 — Limits and handoff

Mention the public-repository scope, first-five-comment cap, incomplete search/context and English keyword limitations. Potential security reports need private review; the final brief omits issue text but Dify execution logs can still contain the earlier tool output. Finish by pointing to the source, actual exported DSL and published Web App.

## Questions to prepare for

- Why a plugin rather than putting every request in HTTP nodes?
- Why explicitly emit `payload_json` instead of relying on generic tool JSON?
- Why are related titles not confirmed duplicates?
- What happens if comment fetch or search fails?
- Why use rules rather than an LLM, and where do those rules stop working?
- Why can a UI draft and API execution differ?
- Why are the two end outputs named `report` and `attention_report`?
- What can remain in execution logs after the security branch?

Before submitting, play the final video as a viewer, verify intelligible English audio and a visible complete Workflow execution, and use the final candidate-narrated video link. The current MP4 is silent and clearly labeled as a recording template.
