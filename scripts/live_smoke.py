"""Actual SDK + live GitHub API smoke test, NOT a Dify platform execution."""
import argparse,json,sys,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'plugin'),str(ROOT/'workflow')]
from tools.read_issue import ReadIssueTool
from tools.related_issues import RelatedIssuesTool
from inspect_issue import main as inspect
from render_report import main as render

def variables(messages):
    return {m.message.variable_name:m.message.variable_value for m in messages if m.type.value=='variable'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('repository');parser.add_argument('issue_number');parser.add_argument('--output',type=Path,default=ROOT/'docs/live-smoke.json')
    args=parser.parse_args()
    credentials={'github_token':os.environ.get('GITHUB_TOKEN','')}
    steps=[]
    read=variables(ReadIssueTool.from_credentials(credentials).invoke({'repository':args.repository,'issue_number':args.issue_number}))
    steps.append({'name':'read_issue','status':read['status']})
    route=inspect(read['payload_json'])
    steps.append({'name':'inspect_issue','route':route['route']})
    if route['route']=='continue':
        related=variables(RelatedIssuesTool.from_credentials(credentials).invoke({'repository':args.repository,'keywords':route['keywords'],'exclude_number':args.issue_number}))
        steps.append({'name':'related_issues','status':related['status']})
        report=render(route['context_json'],related['payload_json'])['report']
        steps.append({'name':'render_report','status':'ok'})
    else:report=route['report']
    result={'verification_scope':'Local Python SDK invocation with live GitHub API; not execution in Dify Cloud.','checked_at':datetime.now(timezone.utc).isoformat(),'repository':args.repository,'issue_number':args.issue_number,'steps':steps,'report':report}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps({'steps':steps,'saved':str(args.output)}))
    if read['status']!='ok':return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
