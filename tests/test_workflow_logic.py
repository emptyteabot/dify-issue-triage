import json
from inspect_issue import main as inspect
from render_report import main as render

def envelope(title='Workflow fails',body=''):
    return json.dumps({'ok':True,'repository':'a/b','issue':{'number':1,'title':title,'body':body,'url':'https://github.com/a/b/issues/1','state':'open','updated_at':'2026-10-13'},'comments':[],'warnings':[]})

def test_security_report_not_reproduced():
    out=inspect(envelope('API endpoint exposes other users API keys','private PoC'))
    assert out['route']=='stop' and 'private PoC' not in out['report']

def test_template_headings_do_not_count_as_answers():
    out=inspect(envelope(body='### Version\n### Steps to reproduce\n### Error'))
    assert len(json.loads(out['context_json'])['missing'])==4

def test_connectivity_branch_and_degraded_search():
    out=inspect(envelope('connection refused after upgrade','Docker 1.9.0\n1. Run the workflow'))
    assert json.loads(out['context_json'])['category']=='connectivity'
    report=render(out['context_json'],json.dumps({'ok':False,'error':{'message':'rate limited'}}))['report']
    assert 'Search unavailable' in report and 'connection' in report and 'API-key validation' in report

def test_api_error_is_not_diagnosed():
    out=inspect(json.dumps({'ok':False,'error':{'code':'not_found','message':'Not found'}}))
    assert out['route']=='stop' and 'No diagnosis' in out['report']

def test_related_reports_are_candidates():
    out=inspect(envelope('429 response','Dify Cloud 1.9.0'))
    report=render(out['context_json'],json.dumps({'ok':True,'query':'repo:a/b is:issue 429','items':[],'incomplete_results':False}))['report']
    assert 'does not prove' in report and 'not confirmed duplicates' in report
