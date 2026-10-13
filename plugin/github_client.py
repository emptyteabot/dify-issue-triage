"""Bounded, read-only GitHub REST calls. No Dify dependency in this module."""
import re
from typing import Any
import httpx

API_ROOT = 'https://api.github.com'
REPOSITORY = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9_.-]{1,100}\Z')

class GitHubError(Exception):
    def __init__(self, code: str, message: str, **details: Any):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details
    def envelope(self):
        return {'ok': False, 'error': {'code': self.code, 'message': self.message, **self.details}}

def repository_name(value):
    value = str(value or '').strip()
    if not REPOSITORY.fullmatch(value) or value.split('/')[1] in {'.', '..'}:
        raise GitHubError('invalid_input', 'Repository must be owner/repository, without a URL or extra path.')
    return value

def positive_integer(value):
    if isinstance(value, bool) or not re.fullmatch(r'[1-9][0-9]{0,9}', str(value)):
        raise GitHubError('invalid_input', 'Issue number must be a positive integer.')
    return int(value)

def redact(text, limit=10000):
    """Best effort, not a general-purpose secret scanner."""
    text = str(text or '')
    text = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{15,}|github_pat_[A-Za-z0-9_]{15,}|sk-[A-Za-z0-9_-]{16,})', '[REDACTED]', text)
    text = re.sub(r'(?i)\b(Bearer\s+)\S+', r'\1[REDACTED]', text)
    return text[:limit] + ('\n[truncated]' if len(text) > limit else '')

def search_terms(value):
    words = re.findall(r'[A-Za-z0-9][A-Za-z0-9_-]{2,29}', redact(value, 300).lower())
    stop = {'the','and','with','from','this','that','when','after','before','bug','dify','error','issue','http','https','repo','github','com'}
    return ' '.join(list(dict.fromkeys(w for w in words if w not in stop))[:3]) or 'workflow'

class GitHubClient:
    def __init__(self, token='', *, transport=None):
        headers = {'Accept':'application/vnd.github+json', 'X-GitHub-Api-Version':'2022-11-28', 'User-Agent':'dify-issue-triage/0.1.0'}
        if token and token.strip():
            headers['Authorization'] = f'Bearer {token.strip()}'
        self.http = httpx.Client(base_url=API_ROOT, headers=headers, timeout=httpx.Timeout(15.0, connect=5.0), follow_redirects=False, transport=transport)
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.http.close()
    def get(self, path, params=None):
        try:
            response = self.http.get(path, params=params)
        except httpx.TimeoutException:
            raise GitHubError('timeout', 'GitHub timed out. Retry later.') from None
        except httpx.RequestError:
            raise GitHubError('network_error', 'Could not reach GitHub. Check outbound HTTPS connectivity.') from None
        status = response.status_code
        detail = {'http_status': status, 'request_id': response.headers.get('x-github-request-id','')}
        if status == 401:
            raise GitHubError('unauthorized', 'GitHub rejected the token. Check expiry, or remove it for public access.', **detail)
        if status == 429 or (status == 403 and (response.headers.get('x-ratelimit-remaining') == '0' or 'rate limit' in response.text.lower())):
            raise GitHubError('rate_limited', 'GitHub rate limit reached. Respect Retry-After or the reset time; do not retry in a tight loop.', retry_after=response.headers.get('retry-after',''), reset_at=response.headers.get('x-ratelimit-reset',''), **detail)
        if status == 403:
            raise GitHubError('forbidden', 'GitHub denied access. Check token permissions and organization policies.', **detail)
        if status == 404:
            raise GitHubError('not_found', 'Repository or issue not found, or not visible to this credential. Check the public repository and issue number.', **detail)
        if 300 <= status < 400:
            raise GitHubError('moved', 'This resource moved. Use its current owner/repository name.', **detail)
        if status >= 400:
            raise GitHubError('upstream_error', 'GitHub returned an error. Retry later; retain the request ID for troubleshooting.', **detail)
        try:
            return response.json()
        except ValueError:
            raise GitHubError('invalid_response', 'GitHub returned an unexpected non-JSON response.', **detail) from None
    def public_repository(self, repository):
        data = self.get(f'/repos/{repository}')
        if not isinstance(data, dict) or 'private' not in data:
            raise GitHubError('invalid_response', 'Unexpected repository metadata.')
        if data['private'] or data.get('visibility','public') != 'public':
            raise GitHubError('private_repository', 'This demo intentionally supports public repositories only.')
    def read_issue(self, repository, number):
        repository, number = repository_name(repository), positive_integer(number)
        self.public_repository(repository)
        issue = self.get(f'/repos/{repository}/issues/{number}')
        if not isinstance(issue, dict) or 'title' not in issue:
            raise GitHubError('invalid_response', 'Unexpected issue data.')
        if 'pull_request' in issue:
            raise GitHubError('pull_request', 'This number identifies a pull request. Choose an issue instead.')
        warnings, comments = [], []
        if issue.get('comments',0):
            try:
                raw = self.get(f'/repos/{repository}/issues/{number}/comments', {'per_page':5,'page':1})
                if not isinstance(raw,list):
                    raise GitHubError('invalid_response','Unexpected comment data.')
                comments = [{'body':redact(c.get('body'),1500),'url':c.get('html_url','')} for c in raw[:5]]
            except GitHubError as exc:
                warnings.append(f'Comments unavailable ({exc.code}); only the issue body is used.')
        if issue.get('comments',0) > len(comments):
            warnings.append('Only the first five comments are requested; later discussion may change the conclusion.')
        return {'ok':True,'repository':repository,'issue':{'number':number,'title':redact(issue['title'],250),'body':redact(issue.get('body')),'url':issue.get('html_url',''),'state':issue.get('state','unknown'),'labels':[redact(x.get('name',''),80) for x in issue.get('labels',[])],'updated_at':issue.get('updated_at',''),'comments_count':issue.get('comments',0)},'comments':comments,'warnings':warnings}
    def related_issues(self, repository, keywords, exclude_number):
        repository, number = repository_name(repository), positive_integer(exclude_number)
        self.public_repository(repository)
        query = f'repo:{repository} is:issue in:title {search_terms(keywords)}'
        data = self.get('/search/issues', {'q':query,'per_page':6})
        if not isinstance(data,dict) or not isinstance(data.get('items'),list):
            raise GitHubError('invalid_response','Unexpected search data.')
        items = [{'number':x['number'],'title':redact(x.get('title'),250),'url':x.get('html_url',''),'state':x.get('state','unknown')} for x in data['items'] if x.get('number') != number and 'pull_request' not in x][:5]
        return {'ok':True,'query':query,'items':items,'incomplete_results':bool(data.get('incomplete_results',False)),'note':'Keyword candidates only; a human must verify whether the cause is actually the same.'}
