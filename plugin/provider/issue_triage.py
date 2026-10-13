from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from github_client import GitHubClient, GitHubError

class IssueTriageProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = str(credentials.get('github_token') or '').strip()
        if not token:
            return
        try:
            with GitHubClient(token) as client:
                client.get('/user')
        except GitHubError as exc:
            raise ToolProviderCredentialValidationError(exc.message) from None
