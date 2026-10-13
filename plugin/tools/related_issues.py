import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from github_client import GitHubClient, GitHubError

class RelatedIssuesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            with GitHubClient(str(self.runtime.credentials.get('github_token') or '')) as client:
                result = client.related_issues(tool_parameters.get('repository'), tool_parameters.get('keywords'), tool_parameters.get('exclude_number'))
        except GitHubError as exc:
            result = exc.envelope()
        yield self.create_variable_message('status', 'ok' if result['ok'] else 'error')
        yield self.create_variable_message('payload_json', json.dumps(result, ensure_ascii=False))
        yield self.create_json_message(result)
        yield self.create_text_message('GitHub request completed.' if result['ok'] else result['error']['message'])
