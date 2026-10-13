"""Code node 2: combine evidence and search results into a reviewable report."""
import json
import re


def safe(value):
    return re.sub(r'([\\`*_{}\[\]<>])',r'\\\1',str(value)).replace('\n',' ')


def main(context_json: str, related_json: str) -> dict:
    context, related = json.loads(context_json), json.loads(related_json)
    issue = context['issue']
    lines=['# Issue triage brief','',f"**{safe(context['repository'])} #{issue['number']} — {safe(issue['title'])}**",f"Source: {issue['url']}",f"State: {issue['state']} · Last updated: {issue['updated_at']}",'',f"Triage signal: **{context['category']}** (rule-based; not a root-cause diagnosis)",'','## Information to confirm']
    lines += ['- '+x for x in context['missing']] or ['- Basic context signals are present. Verify their values and reproducibility manually.']
    lines += ['','## Suggested investigation order'] + [f'{i}. {x}' for i,x in enumerate(context['checks'],1)]
    lines += ['','## Related reports']
    if related.get('ok'):
        lines += [f"- #{x['number']} [{safe(x['title'])}]({x['url']}) — {x['state']}" for x in related['items']] or ['- No candidates matched this limited title search. This does not prove the issue is new.']
        lines += ['',f"Search: `{related['query']}`",'These are keyword candidates, not confirmed duplicates.']
        if related.get('incomplete_results'):
            lines.append('GitHub marked this search incomplete.')
    else:
        lines += ['Search unavailable: '+related.get('error',{}).get('message','Unknown error.'),'The brief remains usable without search results.']
    lines += ['','## Suggested reply — review before posting','Thanks for reporting this. I have not confirmed the cause yet.']
    if context['missing']:
        lines += ['Could you share the following so we can reproduce it?'] + ['- '+x for x in context['missing']]
    else:
        lines += ['The report includes basic context. Could you confirm whether the smallest reproduction still fails and share its run ID?']
    lines += ['Please redact credentials and personal data from logs. '+context['checks'][0],'','## Limits','Read-only workflow. No issue comment, label, or state is changed. Context is bounded to the issue body and the first five comments. English keyword rules can miss multilingual or unusual reports.']
    lines += ['- '+x for x in context['warnings']]
    return {'report':'\n'.join(lines)}
