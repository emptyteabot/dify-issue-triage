# GitHub Issue Triage

Two read-only tools for public GitHub issue triage: `read_issue` retrieves an issue and the first five comments; `related_issues` searches titles in that repository.

Install the `.difypkg` through Dify's plugin installation menu. In Integrations > Tools, configure GitHub Issue Triage. Leave the optional token blank for anonymous public reads, or configure a GitHub personal token in the secret credential field. No write permissions are needed.

Example: repository `langgenius/dify`, issue number as a positive integer string. Both tools expose `status` and `payload_json`. Expected API failures return an `ok: false` envelope with an actionable error code. Credentials are never workflow inputs.

See the repository README for installation, the complete workflow, testing and limitations.
