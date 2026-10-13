# Verification record

This record separates automated tests, live SDK requests and actual Dify execution.

## Automated checks

- Python 3.12, Dify Plugin SDK 0.10.2, httpx 0.28.1.
- `pytest`: **31 passed**. Two warnings originated from SDK/gevent/Pydantic integration; no test failure.
- Official plugin CLI 0.6.11 packaged the plugin successfully.
- The local smoke check invoked both real SDK tool adapters against GitHub's live public API. See `live-smoke.json` for its own bounded scope.

## Installed package and actual export

- Dify Cloud installed **emptyteabot/issue_triage 0.1.0** as a local plugin.
- Both **Read public issue** and **Find related issues** appeared in the provider.
- A blank-token credential profile, **Anonymous public access**, was saved and used through workspace default authorization.
- The actual DSL was exported from Dify after successful execution and publication; its version is **0.7.0**.
- The package checksum in that export is:

```text
emptyteabot/issue_triage:0.1.0@26b10d4bee0f1d0c97a58c3748163e39a93ef23679c2441bcbe438edaac780de
```

The official CLI produced the same checksum for the committed package. No API key or workspace credential value is present in the export.

## Successful Studio run

Input: `repository=langgenius/dify`, `issue_number=36283`.

The Dify UI displayed **SUCCESS**, **2.759 seconds**, **0 Tokens**, and **7 executed nodes**. Its displayed start time was `2026-10-13 23:19:50` in the browser's Asia/Tokyo timezone (22:19:50 Asia/Shanghai).

| Node | Displayed elapsed time |
| --- | --- |
| Repository and issue | 0.078 ms |
| Read public issue | 1.486 s |
| Inspect and route | 79.324 ms |
| Continue public triage? | 0.112 ms |
| Find related issues | 513.961 ms |
| Compose evidence brief | 78.782 ms |
| Triage brief | 0.093 ms |

Node elapsed times do not include all orchestration overhead and therefore need not sum to the displayed total runtime.

The result used real source issue metadata and returned a connectivity signal, investigation order, five keyword candidates and an English reply draft. The source issue was already closed; this workflow did not change its state.

## Error path

Input: `repository=not a repo`, `issue_number=1`.

The result was `invalid_input` with the repository-format explanation and “No diagnosis was generated.” The stop path handled the failure. End outputs are named `report` for ordinary triage and `attention_report` for errors/private review, because Dify publishing requires output variable names to be unique across end nodes.

## Published app and access

[Published Web App](https://udify.app/workflow/5SgEngzA4VeBZeH3)

The published Web App completed a separate full run against the same public issue and displayed all seven successful steps and the resulting brief. A separate HTTP request with no cookies or authentication returned **200** for the exact public app URL. This verifies public page access; an anonymous API integration key was not created or exposed.

## Video

`media/walkthrough-captioned.mp4` is an edited English-captioned screen-capture walkthrough. It includes captured input, execution and result screens from the actual public run, the Studio success trace, and the invalid-input run. The underlying captured frames are preserved in `media/capture-source.zip`. No execution result or interface was fabricated.

The video has **no audio narration**. The candidate must add their own spoken English explanation before treating it as the final candidate walkthrough.
