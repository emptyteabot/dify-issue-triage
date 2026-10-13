# Privacy

This plugin sends public repository names, issue numbers and sanitized search terms to api.github.com over HTTPS. If configured, a GitHub token is sent only in the Authorization header. The plugin performs GET requests only and refuses private repositories. It does not use analytics or persistent storage and does not print tokens or raw HTTP errors.

Issue bodies, selected comments, metadata and search results are returned to the Dify workspace. Dify may retain these values in execution logs under the workspace's own policies. Common token patterns are redacted on a best-effort basis, not as a guarantee. Do not use public reports to exchange secrets or private vulnerability details. Operators are responsible for workspace permissions and log retention.
