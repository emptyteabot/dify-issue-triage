"""Build the importable DSL. The final submission should be re-exported from Dify."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]

def node(id,kind,title,x,y,**extra):
    return {'id':id,'type':'custom','data':{'type':kind,'title':title,'desc':'','selected':False,**extra},'position':{'x':x,'y':y},'positionAbsolute':{'x':x,'y':y},'width':244,'height':110,'sourcePosition':'right','targetPosition':'left','selected':False}

def mixed(value):return {'type':'mixed','value':value}

def tool(id,title,name,x,y,params):
    return node(id,'tool',title,x,y,provider_id='emptyteabot/issue_triage/issue_triage',provider_name='emptyteabot/issue_triage/issue_triage',provider_type='builtin',plugin_id='emptyteabot/issue_triage',tool_name=name,tool_label=title,tool_description='Read-only GitHub API operation.',tool_configurations={},tool_parameters={k:mixed(v) for k,v in params.items()},tool_node_version='2',is_team_authorization=True)

def code(id,title,file,x,y,inputs,outputs):
    return node(id,'code',title,x,y,code_language='python3',code=(ROOT/'workflow'/file).read_text(),variables=[{'variable':k,'value_selector':v,'value_type':'string'} for k,v in inputs.items()],outputs={k:{'type':'string','children':None} for k in outputs})

nodes=[
 node('start','start','Repository and issue',40,200,variables=[{'variable':'repository','label':'Public repository (owner/repository)','type':'text-input','required':True,'max_length':140,'options':[]},{'variable':'issue_number','label':'Issue number','type':'text-input','required':True,'max_length':10,'options':[]}]),
 tool('read','Read public issue','read_issue',370,200,{'repository':'{{#start.repository#}}','issue_number':'{{#start.issue_number#}}'}),
 code('inspect','Inspect and route','inspect_issue.py',700,200,{'payload_json':['read','payload_json']},['route','keywords','context_json','report']),
 node('route','if-else','Continue public triage?',1030,200,cases=[{'id':'true','case_id':'true','logical_operator':'and','conditions':[{'id':'is-normal','varType':'string','variable_selector':['inspect','route'],'comparison_operator':'is','value':'continue'}]}]),
 tool('related','Find related issues','related_issues',1360,80,{'repository':'{{#start.repository#}}','keywords':'{{#inspect.keywords#}}','exclude_number':'{{#start.issue_number#}}'}),
 code('compose','Compose evidence brief','render_report.py',1690,80,{'context_json':['inspect','context_json'],'related_json':['related','payload_json']},['report']),
 node('done','end','Triage brief',2020,80,outputs=[{'variable':'report','value_selector':['compose','report'],'value_type':'string'}]),
 node('stop','end','Error or private review',1360,440,outputs=[{'variable':'attention_report','value_selector':['inspect','report'],'value_type':'string'}])]
byid={n['id']:n for n in nodes}
edges=[]
for source,target,handle in [('start','read','source'),('read','inspect','source'),('inspect','route','source'),('route','related','true'),('related','compose','source'),('compose','done','source'),('route','stop','false')]:
    edges.append({'id':f'{source}-{handle}-{target}-target','source':source,'target':target,'sourceHandle':handle,'targetHandle':'target','type':'custom','zIndex':0,'data':{'sourceType':byid[source]['data']['type'],'targetType':byid[target]['data']['type'],'isInIteration':False,'isInLoop':False}})
features={'file_upload':{'enabled':False,'allowed_file_extensions':[],'allowed_file_types':[],'allowed_file_upload_methods':[],'number_limits':3},'opening_statement':'','retriever_resource':{'enabled':False},'sensitive_word_avoidance':{'enabled':False},'speech_to_text':{'enabled':False},'suggested_questions':[],'suggested_questions_after_answer':{'enabled':False},'text_to_speech':{'enabled':False,'language':'','voice':''}}
app={'app':{'name':'GitHub Issue Triage','description':'Public issue context, related reports and an evidence-first reply draft. Read-only, rule-based, no LLM key required.','mode':'workflow','icon':'🔎','icon_background':'#DDF7ED','use_icon_as_answer_icon':False},'kind':'app','version':'0.3.1','dependencies':[],'workflow':{'conversation_variables':[],'environment_variables':[],'features':features,'graph':{'nodes':nodes,'edges':edges,'viewport':{'x':10,'y':100,'zoom':0.55}}}}
(ROOT/'workflow/issue-triage.authored.yml').write_text(yaml.safe_dump(app,sort_keys=False,allow_unicode=True,width=110),encoding='utf-8')
print('Built workflow/issue-triage.authored.yml; the verified platform export is not overwritten.')
