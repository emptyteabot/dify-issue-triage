import json
import httpx
import tools.read_issue as adapter
from github_client import GitHubClient

def test_sdk_adapter_emits_workflow_variables_on_real_error(monkeypatch):
    transport=httpx.MockTransport(lambda r:httpx.Response(404,headers={'x-github-request-id':'test-id'}))
    monkeypatch.setattr(adapter,'GitHubClient',lambda token:GitHubClient(token,transport=transport))
    messages=list(adapter.ReadIssueTool.from_credentials({'github_token':'PRIVATE_TOKEN'}).invoke({'repository':'a/b','issue_number':'1'}))
    variables={m.message.variable_name:m.message.variable_value for m in messages if m.type.value=='variable'}
    assert variables['status']=='error'
    assert json.loads(variables['payload_json'])['error']['code']=='not_found'
    assert 'PRIVATE_TOKEN' not in json.dumps([m.model_dump(mode='json') for m in messages])
