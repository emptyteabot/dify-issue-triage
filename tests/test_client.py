import httpx
import pytest
from github_client import GitHubClient, GitHubError, repository_name, positive_integer, redact

@pytest.mark.parametrize('value',['https://github.com/a/b','a/../b','a/b?x=1','a/b/c','a/..'])
def test_bad_repository(value):
    with pytest.raises(GitHubError): repository_name(value)

@pytest.mark.parametrize('value',[0,-1,1.5,True,'1.0','x'])
def test_bad_number(value):
    with pytest.raises(GitHubError): positive_integer(value)

@pytest.mark.parametrize('status,headers,code',[(401,{},'unauthorized'),(403,{},'forbidden'),(403,{'x-ratelimit-remaining':'0'},'rate_limited'),(429,{'retry-after':'60'},'rate_limited'),(404,{},'not_found'),(502,{},'upstream_error'),(301,{},'moved')])
def test_http_failures(status,headers,code):
    transport=httpx.MockTransport(lambda r:httpx.Response(status,headers=headers,json={'message':'private diagnostic SECRET'}))
    with GitHubClient('super-secret',transport=transport) as c:
        with pytest.raises(GitHubError) as e:c.get('/user')
    assert e.value.code==code
    assert 'SECRET' not in str(e.value.envelope()) and 'super-secret' not in str(e.value.envelope())

def test_timeout_is_actionable():
    def fail(r):raise httpx.ReadTimeout('secret-url',request=r)
    with GitHubClient(transport=httpx.MockTransport(fail)) as c:
        with pytest.raises(GitHubError) as e:c.get('/user')
    assert e.value.code=='timeout' and 'secret-url' not in str(e.value)

def test_private_repo_never_fetches_body():
    paths=[]
    def handler(r):
        paths.append(r.url.path);return httpx.Response(200,json={'private':True})
    with GitHubClient(transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(GitHubError) as e:c.read_issue('a/b','1')
    assert e.value.code=='private_repository' and paths==['/repos/a/b']

def test_partial_comments_preserve_issue():
    def handler(r):
        if r.url.path.endswith('/comments'):return httpx.Response(503)
        if '/issues/' in r.url.path:return httpx.Response(200,json={'title':'Timeout','body':'hello','comments':2})
        return httpx.Response(200,json={'private':False})
    with GitHubClient(transport=httpx.MockTransport(handler)) as c:result=c.read_issue('a/b','1')
    assert result['ok'] and result['warnings'] and result['comments']==[]

def test_search_removes_current_issue_and_operators():
    queries=[]
    def handler(r):
        if r.url.path=='/search/issues':
            queries.append(r.url.params['q'])
            return httpx.Response(200,json={'items':[{'number':1},{'number':2,'title':'related'}]})
        return httpx.Response(200,json={'private':False})
    with GitHubClient(transport=httpx.MockTransport(handler)) as c:result=c.related_issues('a/b','connection repo:private/secret refused','1')
    assert len(result['items'])==1 and result['items'][0]['number']==2
    assert queries[0].count('repo:')==1

def test_token_only_in_header():
    def handler(r):
        assert r.headers['Authorization']=='Bearer TEST_TOKEN'
        assert 'TEST_TOKEN' not in str(r.url)
        return httpx.Response(200,json={})
    with GitHubClient('TEST_TOKEN',transport=httpx.MockTransport(handler)) as c:c.get('/user')

def test_redaction_and_bounds():
    assert 'ghp_' not in redact('ghp_'+'a'*36)
    assert '[REDACTED]' in redact('Authorization: Bearer PRIVATE')
    assert '[truncated]' in redact('x'*10001)

def test_pull_requests_rejected():
    def handler(r):return httpx.Response(200,json={'private':False} if '/issues/' not in r.url.path else {'title':'PR','pull_request':{}})
    with GitHubClient(transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(GitHubError) as e:c.read_issue('a/b','1')
    assert e.value.code=='pull_request'
