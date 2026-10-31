"""Audit host-delivered lifecycle events without executing or storing raw content."""
import json
import os
import sys
import time
from .engine import digest, receipt
from .full import hook_audit
from .hook import ROOT, repository_git_dir
EVENTS = {'userPromptTransformed', 'postToolUse', 'postToolUseFailure'}

def process(kind, event):
    if kind not in EVENTS or not isinstance(event, dict):
        raise ValueError('invalid lifecycle event')
    started = time.perf_counter_ns()
    battery = hook_audit(event, ROOT)
    directory = repository_git_dir(ROOT) / 'prime-audit'
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or not directory.resolve().is_relative_to(repository_git_dir(ROOT).resolve()):
        raise ValueError('symlinked receipt directory')
    record = receipt({'schema':'prime.lifecycle.v1','event':kind,
        'session_sha256':digest(str(event.get('sessionId',event.get('session_id','')))),
        'event_sha256':digest(event),'full_battery':battery,
        'elapsed_ns':time.perf_counter_ns()-started,'recorded_at_ns':time.time_ns(),
        'raw_text_persisted':False,'executed':False})
    fd=os.open(directory/'lifecycle.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
    os.fchmod(fd,0o600)
    with os.fdopen(fd,'a',encoding='utf-8') as stream:
        stream.write(json.dumps(record)+'\n')
    context = 'PRIME 6.7 audited the available '+kind+' event; receipt '+record['receipt']['sha256']+'. Measurements are not proof of correctness. Use prime_full_audit to inspect the complete task/plan report before operations.'
    if kind == 'userPromptTransformed' and isinstance(event.get('transformedPrompt'), str):
        return {'modifiedTransformedPrompt': event['transformedPrompt']+'\n\n'+context}
    return {'additionalContext':context}

def main():
    try:
        raw=sys.stdin.read(262145)
        if len(raw)>262144: raise ValueError('oversize event')
        result=process(sys.argv[1],json.loads(raw))
    except (ValueError,TypeError,OSError,IndexError):
        result={'additionalContext':'PRIME 6.7 lifecycle audit failed. Do not claim this event was audited; inspect and report the failure.'}
    print(json.dumps(result))
if __name__=='__main__': main()
