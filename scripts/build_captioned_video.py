"""Create an English-captioned recording template from actual Dify screen captures.
No synthesized speech or candidate impersonation is used.
"""
import json, textwrap, subprocess, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'media/captures'
EVIDENCE.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(ROOT/'media/capture-source.zip') as capture_archive:
    for member in capture_archive.infolist():
        if not (EVIDENCE/member.filename).resolve().is_relative_to(EVIDENCE.resolve()):
            raise ValueError('Unsafe capture archive path')
        capture_archive.extract(member,EVIDENCE)
WORK=ROOT.parent/'tmp/video-render'
WORK.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
BG='#101E2A'; WHITE='#F1F6F8'; MUTED='#AEC1CC'; GREEN='#60E3BC'
W,H=1920,1080

def f(size,bold=False,mono=False):return ImageFont.truetype(MONO if mono else BOLD if bold else FONT,size)

def wrapped(draw,text,xy,font,width,fill=WHITE,spacing=14):
    x,y=xy
    words=text.split();line=''
    for word in words:
        trial=(line+' '+word).strip()
        if draw.textlength(trial,font=font)>width and line:
            draw.text((x,y),line,font=font,fill=fill);y+=font.size+spacing;line=word
        else:line=trial
    if line:draw.text((x,y),line,font=font,fill=fill);y+=font.size+spacing
    return y

def render(title,notes,*,screen=None,code=None,intro=False):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.text((38,22),'GitHub Issue Triage',font=f(38,True),fill=WHITE)
    d.text((1410,30),'DIFY SDK + WORKFLOW',font=f(22,True),fill=GREEN)
    d.line((36,85,W-36,85),fill='#294150',width=2)
    d.text((38,1032),'English-captioned recording template | Candidate voice has not been recorded',font=f(22),fill=MUTED)
    if intro:
        d.text((85,220),'Evidence before diagnosis.',font=f(68,True),fill=WHITE)
        y=wrapped(d,'A public GitHub issue becomes a context brief, related reports and a reply draft.',(90,348),f(42),1350)
        d.text((90,y+52),'Real GitHub API. Real Dify execution.',font=f(40,True),fill=GREEN)
        d.text((90,y+122),'Read-only. Human review before posting.',font=f(36),fill=MUTED)
        d.text((90,825),'This edited walkthrough includes captured screens of a complete successful Workflow run.',font=f(28),fill=WHITE)
        return im
    if screen:
        shot=Image.open(screen).convert('RGB')
        shot.thumbnail((1300,895),Image.Resampling.LANCZOS)
        d.rounded_rectangle((34,110,1348,1017),radius=14,fill='#E8F0F4')
        im.paste(shot,(41+(1300-shot.width)//2,116+(895-shot.height)//2))
    else:
        d.rounded_rectangle((35,110,1348,1017),radius=14,fill='#172E40')
        d.text((63,142),'ACTUAL SOURCE EXCERPT',font=f(22,True),fill=GREEN)
        y=205
        for line in (code or '').splitlines():
            for part in textwrap.wrap(line,86,replace_whitespace=False,drop_whitespace=False) or ['']:
                d.text((62,y),part,font=f(24,mono=True),fill=WHITE);y+=32
    y=wrapped(d,title,(1400,135),f(37,True),470,fill=GREEN)
    y+=42
    for note in notes:
        y=wrapped(d,note,(1400,y),f(28),465,spacing=12);y+=36
    return im

entries=[];chapters=[];elapsed=0.0;counter=0

def add_image(image,duration):
    global counter,elapsed
    path=WORK/f'frame-{counter:04d}.png';image.save(path)
    entries.append((path,float(duration)));counter+=1;elapsed+=float(duration)

def chapter(title,notes,duration,*,screen=None,code=None,intro=False,caption=''):
    start=elapsed;add_image(render(title,notes,screen=screen,code=code,intro=intro),duration)
    chapters.append({'start':start,'end':elapsed,'title':title,'caption':caption or ' '.join(notes)})

def recorded(title,notes,folder,caption):
    start=elapsed
    timing=json.loads((EVIDENCE/folder/'timing.json').read_text())
    for i,record in enumerate(timing):
        duration=(timing[i+1]['elapsed_ms']-record['elapsed_ms'])/1000 if i+1<len(timing) else 1.2
        add_image(render(title,notes,screen=EVIDENCE/folder/record['file']),max(duration,0.04))
    chapters.append({'start':start,'end':elapsed,'title':title,'caption':caption})

chapter('01 / The problem',[],12,intro=True,caption='A read-only workflow helps maintainers collect evidence, find related reports and prepare a reply without guessing the cause.')
chapter('02 / A complete tool plugin',[
 'Two callable tools: Read public issue and Find related issues.',
 'The package is installed in Dify Cloud.',
 'An optional secret token is configured at the provider, never as a Workflow input.'
],21,screen=EVIDENCE/'dify-plugin-installed.jpg',caption='The Dify SDK plugin exposes two read-only tools. A token is optional for public API access and is configured as a provider secret.')
client=(ROOT/'plugin/github_client.py').read_text().splitlines()
request_start=next(i for i,line in enumerate(client) if '    def get(' in line)
request_end=next(i for i,line in enumerate(client) if '        status = response.status_code' in line)
code='plugin/github_client.py (selected excerpts)\n\n'+client[5]+'\n\n# Client configuration\n'+next(x for x in client if 'self.http = httpx.Client' in x)+'\n\n# Request handling\n'+'\n'.join(client[request_start:request_end])+'\n        # ... HTTP status handling follows' 
chapter('03 / Bounded API access',[
 'The API host is fixed to api.github.com.',
 'Validate the repository and issue number before requesting data.',
 'Use explicit timeouts. Distinguish authorization, rate limits, missing resources and connectivity failures.'
],25,code=code,caption='Repository syntax is validated before an API call. Requests use a fixed HTTPS host and explicit timeouts, with distinct actionable error codes.')
chapter('04 / Workflow variables',[
 'The SDK emits status and payload_json explicitly.',
 'Expected API failures return an error envelope.',
 'The Workflow reads those variables, branches, then calls the related-search tool.'
],20,code='plugin/tools/read_issue.py (_invoke excerpt)\n\n'+'\n'.join((ROOT/'plugin/tools/read_issue.py').read_text().splitlines()[7:17]),caption='The tool adapter returns status and payload_json as explicit SDK variables. The Workflow parses the payload and routes expected errors instead of inventing a diagnosis.')
recorded('05 / Complete live execution',[
 'Input: langgenius/dify, issue 36283.',
 'This is the published Web App executing the actual plugin.',
 'The capture shows input, execution and the final result in order.'
],'public-run','Now the published Web App runs the entire Workflow against a real public GitHub issue. Captured screens show the real input, execution and result; this walkthrough is edited for presentation.')
chapter('06 / Inspect the real trace',[
 'All seven executed nodes succeeded.',
 'The Studio test took 2.759 seconds and used zero model tokens.',
 'Both plugin tools ran; the Workflow also inspected, branched and composed the report.'
],17,screen=EVIDENCE/'workflow-success-trace.jpg',caption='The Studio trace shows seven successful nodes in 2.759 seconds, with zero model tokens. Both API tools and the processing and conditional nodes executed.')
chapter('07 / Review the evidence',[
 'The report links back to the original issue.',
 'A connectivity signal selects an investigation checklist.',
 'Basic context signals still require human verification.'
],20,screen=EVIDENCE/'web-app-success.jpg',caption='The result identifies the source issue, reports a rule-based connectivity signal and proposes an investigation order. These are triage signals, not a confirmed root cause.')
chapter('08 / Candidates and a draft reply',[
 'Related titles are candidates, not confirmed duplicates.',
 'The draft reply asks for useful evidence and makes no promise of a fix.',
 'No comment, label or issue state is changed.'
],21,screen=EVIDENCE/'web-app-reply.jpg',caption='Related reports are keyword candidates only. The reply remains a draft for review, and the workflow never posts it or changes the issue.')
recorded('09 / Invalid input',[
 'Input: not a repo, issue 1.',
 'Validation returns invalid_input.',
 'The stop branch provides an actionable result without generating a diagnosis.'
],'run-invalid','An invalid repository is handled by the stop branch. The result explains the required input format and explicitly says that no diagnosis was generated.')
chapter('10 / Limits and submission',[
 'Only public repositories and the first five comments are supported.',
 'English keyword rules and title search have known limits.',
 'Review the source and exported DSL. Add the candidate\'s own English voice before final submission.'
],20,code='Delivered\n\nplugin/                 Dify SDK source\nworkflow/issue-triage.yml  Actual Dify export\ndocs/issue-triage-answers.md\nmedia/walkthrough-captioned.mp4\n\nVerified Web App\nhttps://udify.app/workflow/5SgEngzA4VeBZeH3\n\nPublic repository\nhttps://github.com/emptyteabot/dify-issue-triage',caption='The source, exported DSL and tested Web App are available. This captioned recording template has no candidate narration; add your own spoken English explanation before submitting it as the candidate walkthrough.')

def stamp(seconds):
    ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

srt=[]
for i,c in enumerate(chapters,1):
    srt.append(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(textwrap.wrap(c['caption'],78))+'\n')
(ROOT/'media/walkthrough-captions.srt').write_text('\n'.join(srt))
(ROOT/'media/walkthrough-chapters.json').write_text(json.dumps(chapters,indent=2))
concat=WORK/'frames.txt'
concat.write_text(''.join(f"file '{p.as_posix()}'\nduration {duration:.6f}\n" for p,duration in entries)+f"file '{entries[-1][0].as_posix()}'\n")
output=ROOT/'media/walkthrough-captioned.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(ROOT/'media/walkthrough-captions.srt'),'-map','0:v','-map','1:0','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-r','24','-c:s','mov_text','-metadata:s:s:0','language=eng','-metadata','title=GitHub Issue Triage - English-captioned recording template','-movflags','+faststart',str(output)],check=True)
print(json.dumps({'output':str(output),'duration_seconds':elapsed,'bytes':output.stat().st_size,'chapters':len(chapters),'candidate_narration':False}))
