"""Code node 1: route errors/security and collect conservative triage signals."""
import json
import re


def main(payload_json: str) -> dict:
    data = json.loads(payload_json)
    if not data.get('ok'):
        err = data.get('error', {})
        return {'route':'stop','keywords':'','context_json':'{}','report':'## Unable to retrieve issue\n\n' + err.get('message','Unexpected error.') + '\n\nError code: ' + err.get('code','unknown') + '\n\nNo diagnosis was generated.'}
    issue = data['issue']
    text = issue['title'] + '\n' + issue['body'] + '\n' + '\n'.join(x['body'] for x in data.get('comments',[]))
    if re.search(r'(?i)(expos\w*.{0,60}(api.?key|token|secret)|other users?.{0,50}(key|token)|credential leak|security vulnerability|unauthorized access|remote code execution)', text):
        return {'route':'stop','keywords':'','context_json':'{}','report':'## Potential security report: private review required\n\nA keyword rule flagged this report; this is not a confirmed vulnerability. Do not request a public PoC, additional keys or exploitation details. Use the repository\'s published private security reporting channel. Escalate to its security maintainers.\n\n### Suggested public reply\nThanks for flagging this. Please avoid posting further reproduction details or credentials publicly. Please use this repository\'s Security policy or private vulnerability reporting channel so the security team can investigate safely.\n\nIssue text is intentionally omitted from this report. Dify execution logs can still contain the tool output: restrict log access.'}
    missing = []
    if not re.search(r'(?i)\b(?:v?\d+\.\d+\.\d+)\b',text):
        missing.append('Exact Dify version and plugin/provider version (and previous version if this followed an upgrade)')
    if not re.search(r'(?i)docker|self.host|dify cloud|cloud.dify|kubernetes|\bk8s\b|source deployment',text):
        missing.append('Deployment type: Dify Cloud, Docker, Kubernetes, or source deployment')
    if not re.search(r'(?im)^\s*(?:\d+[.)]\s+\S|curl\s+\S)|```(?:python|bash|json|sh)?\s*\n\S',text):
        missing.append('A minimal reproducible input and exact steps, with expected and actual output')
    if not re.search(r'(?i)traceback|request.?id\s*[:=]\s*\S|\b(?:400|401|403|404|429|500|502|503)\b|connection refused|timed? ?out',text):
        missing.append('Exact sanitized error and relevant node/service logs, including timestamp and request/run ID')
    category, checks, keywords = 'needs-investigation', ['Reproduce with the smallest input and compare the expected result with the first failing step.','Locate the boundary that fails before assigning ownership to Dify, the plugin, or the upstream service.'], issue['title']
    if re.search(r'(?i)429|rate.?limit|insufficient_quota',text):
        category='upstream-limit-or-quota'; keywords='429'
        checks=['Inspect the upstream error code: quota/billing exhaustion and request/token rate limits require different fixes.','Compare provider project, model, concurrency, retries, timestamps, and rate-limit headers.','Run one minimal provider request from the same runtime/network with the same credential. Respect Retry-After; never loop on exhausted quota.']
    elif re.search(r'(?i)connection refused|econnrefused',text):
        category='connectivity'; keywords='connection refused'
        checks=['Identify the refusing host and port from sanitized logs; a refused TCP connection happens before API-key validation.','Check service health, container DNS/ports, and whether localhost refers to the wrong container.','Compare the previous and current Dify/plugin-daemon versions, release notes and effective environment configuration.']
    elif re.search(r'(?i)401|unauthori[sz]ed|invalid.api.key',text):
        category='authentication'; keywords='401'
        checks=['Confirm provider, endpoint and credential source without printing the token.','Check expiry, permissions and selected project; compare one minimal request from the same network.']
    elif re.search(r'(?i)\bapi\b',text) and re.search(r'(?i)empty|different|\bui\b',text):
        category='ui-api-parity'; keywords='api empty'
        checks=['Compare the UI draft with the published workflow behind the API key, including app ID and publish time.','Compare input names/types, user/conversation identity, file upload IDs and environment variables.','Compare node traces and parse the final SSE event when response_mode is streaming.']
    elif re.search(r'(?i)documentation|\bdocs?\b',text):
        category='documentation'; keywords='documentation'
        checks=['Reproduce the exact documented example on its stated version, starting with prerequisites.','If version-specific, document the affected range and validate the correction on supported versions.']
    context={'repository':data['repository'],'issue':{k:issue[k] for k in ['number','title','url','state','updated_at']},'category':category,'missing':missing,'checks':checks,'warnings':data.get('warnings',[])}
    return {'route':'continue','keywords':keywords[:250],'context_json':json.dumps(context),'report':''}
