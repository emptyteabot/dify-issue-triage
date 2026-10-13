# Issue Triage Assessment

These are investigation plans and suggested English replies. They do not claim a reproduction or a confirmed diagnosis. Sanitized evidence should be requested narrowly; credentials, full environment files and private customer data should not be posted publicly.

## Issue 1 — “Dify doesn't work. OpenAI doesn't work.”

1. **Is the information sufficient?** No. The failing layer, exact operation and observed error are unspecified. “Installed yesterday” does not identify the release or deployment.
2. **Information needed:** Dify version and deployment method; OpenAI provider/plugin version; whether credential validation or a workflow node fails; model and API base URL; exact sanitized error; minimal reproduction, timestamp and relevant node/service log.
3. **First checks:** Locate the first failing operation. Verify the provider and selected model, inspect the actual upstream status/error code, then compare one minimal OpenAI request from the same runtime/network using the same credential. Check network/proxy, endpoint, account/project access and billing only as supported by the error. Keep the API key out of commands shown publicly.
4. **Reply:**

> Could you share your Dify version, deployment method, selected OpenAI model, and the exact error with secrets removed? Please also tell us whether this happens when saving the provider credentials or when running a workflow, and include the failing node's log and a minimal reproduction. That will let us identify whether the failure is in configuration, connectivity, the provider request or Dify itself. Please do not post your API key.

## Issue 2 — Plugin stopped after upgrade; “connection refused”

1. **First check:** Identify the destination host/port and which service generated the error. A refused TCP connection precedes HTTP authentication; changing an API key is not the first step.
2. **Possible causes:** An unhealthy or absent plugin daemon/upstream service; changed port, hostname or network; `localhost` pointing at the wrong container; stale effective configuration; migration/startup failure; or a Dify/plugin/SDK compatibility change. The upgrade timing is a clue, not proof of the cause.
3. **Information needed:** Previous/current Dify and plugin-daemon versions, plugin identifier/version, deployment method, the sanitized error with host/port, relevant API/worker/plugin-daemon logs and upgrade steps. Ask only for relevant non-secret configuration values.
4. **Order:** Check release notes and upgrade requirements; service/container health; connectivity from the calling service to the named destination; effective DNS/ports/configuration; then a minimal invocation and version compatibility. Reproduce on the same upgrade path. A rollback should be a controlled recovery decision, considering migrations and backups, rather than a blind first action.
5. **Reply:**

> Please share the previous and current Dify/plugin-daemon versions, the plugin ID/version, your deployment method, and the sanitized `connection refused` log including the destination host and port. First, we should verify that the target service is running and reachable from the component making the request. Please include the relevant startup and plugin invocation logs around the upgrade. Once that boundary is clear, we can check configuration changes or a compatibility regression.

## Issue 3 — UI works; API node output is empty

1. **Compare first:** App/workflow IDs, draft versus published graph and publication time, node versions and credential binding, API input names/types, file upload IDs, environment variables and user/conversation identity. Compare both node traces, not just the final screen output.
2. **Are executions necessarily identical?** No. The UI may run a newer draft while the API calls the last published version. Identity, conversation history, files, credentials, runtime values, model nondeterminism and response parsing can differ despite matching visible input.
3. **Verify:** Publish the intended graph, reduce to a minimal failing node, capture both run IDs and resolved inputs/outputs, and repeat with identical effective parameters. For streaming API responses, inspect all SSE events and the final workflow result; an intermediate or incorrectly parsed event can look empty.
4. **Information needed:** Sanitized DSL, publish time, app ID, exact API request and response mode, full sanitized response/SSE sequence, both run IDs and the failing node's input/output/error. Do not request the API key itself.
5. **Reply:**

> Could you confirm whether the UI run uses a draft and when that workflow was last published? Please share the app ID, a sanitized API request/response, response mode, both run IDs, and the node traces for the empty node. We will compare the published graph and the resolved inputs, including input types, file IDs and user/conversation context. If the API streams, please include the final workflow event so we can rule out a response-parsing issue.

## Issue 4 — OpenAI returns 429 after an update

1. **Necessarily a Dify bug?** No. The underlying response must be inspected before assigning ownership.
2. **Possible causes:** Provider request/token limits, exhausted quota or billing restrictions, increased concurrency, retries, changed model/project credentials, or a Dify/plugin update changing request frequency or error handling. An update can contribute even when the limit is enforced upstream.
3. **Ownership evidence:** Capture the upstream error code, request ID and rate-limit headers. Compare request rate and payload at Dify, plugin and OpenAI boundaries. Reproduce one minimal request from the same network and with the same provider account/project. A direct request succeeding once does not rule out a concurrency-dependent failure.
4. **Verification:** Repeat under matched concurrency and token volume, compare pre/post versions and provider usage. Respect `Retry-After` or backoff for transient limits; quota exhaustion needs an account/quota fix, not repeated retries.
5. **Reply:**

> A 429 can indicate either a rate limit or an account/quota problem, so we need the upstream error code before concluding this is an update regression. Please share the sanitized error, request ID, model, Dify/plugin versions and the approximate concurrency when it happens. We will compare the actual request volume and provider response before and after the update. Please avoid repeated retries while quota is exhausted, and do not post credentials.

## Issue 5 — Add an unsupported model provider

1. **Information needed:** Exact provider/model, official API documentation, required capabilities (chat, streaming, tools, embeddings, vision), authentication and endpoint format, hosted/self-hosted constraints, present workaround, number of affected users and the concrete blocked workflow/deadline. Ask whether OpenAI compatibility is actually documented and sufficient.
2. **Prioritization:** Assess verified user impact, frequency, strategic fit, existing requests/workarounds, implementation/maintenance cost and provider stability. Competitor support and urgency are context, not enough evidence to promise a deadline.
3. **Engineering handoff:** Create a concise internal requirement with use case, impact, capability matrix, API/docs links, reproducible gap, acceptance criteria, dependencies and open questions. Link related requests. Explore a provider plugin or contribution path and involve the model-integration owner. Do not imply delivery is committed.
4. **Reply:**

> Which provider and models do you need, and which workflow is blocked? Please share the official API documentation and required capabilities, especially streaming, tool calling, embeddings or vision. It would also help to understand your deployment, affected users, deadline and whether an existing compatible-provider setup works. We can use that information to evaluate a provider plugin or route a concrete integration request to the model-integration team. I cannot commit to a delivery date before that review.

## Issue 6 — Possible exposure of other users' API keys

1. **First action:** Treat it as a potential security incident. Avoid quoting or redistributing the PoC, stop public technical discussion, and notify the security/incident response owner through the established private process. Ask an authorized maintainer to restrict/remove publicly exposed secrets or exploit details while preserving evidence in a restricted location.
2. **Public PoC?** No. Use the repository's verified Security policy/private vulnerability reporting channel. Do not test against other users or request real keys. Any validation should be authorized and use controlled accounts.
3. **Escalation:** Security maintainers/incident response first, with the relevant API/authentication engineering owner. Include affected versions, endpoint and reporter contact privately. Assess scope and credential rotation with security; do not publicly confirm an unverified vulnerability or impact.
4. **Reply:**

> Thank you for reporting this. Please do not post further PoC details, API keys or other users' information in this public issue. Please use this repository's Security policy or private vulnerability reporting channel so the security team can investigate. I am escalating the report through that process. Please avoid testing against accounts or data you do not own or have permission to test.

## Issue 7 — Official documentation example does not work

1. **First verification:** Obtain the exact page/section, copied example, Dify/plugin/runtime versions, deployment, prerequisites and sanitized error. Reproduce the documented commands in a clean environment with the same supported version; check whether the example or a prerequisite changed.
2. **If documentation is wrong:** Record the minimal reproduction, provide a tested temporary correction, file/link the documentation fix, and validate the revised example. Add an executable example check where practical. Explain the correction without blaming the reporter.
3. **If version-specific:** Document the affected range and version prerequisites, supply the working equivalent for relevant supported versions, and link the change/release note. Escalate separately if the product breaks its documented compatibility contract.
4. **Reply:**

> Please share the documentation URL and section, your Dify/plugin versions, the copied example and the exact sanitized error. I will reproduce the example with its stated prerequisites and version. If the example is incorrect, I will provide a verified correction and link the documentation change. If it only fails on certain versions, we will make that version requirement explicit and document the working alternative.

## Issue 8 — Installed plugin, but no tool appears

1. **Possible causes:** The plugin provides a model, endpoint, trigger or agent strategy rather than a tool; it was installed in another workspace; provider initialization/loading failed; credentials are not configured; access permissions differ; manifest `plugins.tools`/provider `tools` references are wrong; or the runtime/plugin version is incompatible. A successful install notification alone does not prove tool registration.
2. **User checks:** Plugin type and ID/version, active workspace, installed-provider detail, credential status, search/filter settings and the workflow node selector's tool category. Check workspace role and relevant startup logs rather than reinstalling immediately.
3. **Reproduce:** Install the exact package/version in a clean workspace on the same Dify release, inspect manifest paths and provider YAML, verify SDK loading/startup, and add the tool to a minimal workflow. Compare installed-plugin status with actual registered tool inventory.
4. **Reply:**

> Could you share the plugin ID/version, Dify version, active workspace, and where you are looking for the tool? Please first check that this is a Tool plugin and that its provider appears under Integrations > Tools in the same workspace. Then confirm its credential status and clear any tool filters. If it still does not appear in the workflow tool selector, please share the relevant sanitized plugin startup/load error so we can check registration and compatibility.

## Reference points

- [Dify documentation](https://docs.dify.ai/)
- [Dify tool plugin specification](https://docs.dify.ai/en/develop-plugin/features-and-specs/plugin-types/tool)
- [Dify repository Security policy](https://github.com/langgenius/dify/security/policy)
- [GitHub responsible vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/about-coordinated-disclosure-of-security-vulnerabilities)

Use the current official policy for the affected repository; do not invent a security email or promise an unverified fix.
