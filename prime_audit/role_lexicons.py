"""Seven lexical cue tables; matching is literal, not a semantic judgment."""
import re
from collections import Counter

ROLES = {
 'evidence': {'stage':'triage', 'pairs':[('trace','obscure'),('verify','assume'),('cite','omit'),('compare','ignore')]},
 'perception': {'stage':'source-review', 'pairs':[('see','overlook'),('observe','ignore'),('hear','miss'),('listen','disregard')]},
 'boundary': {'stage':'preflight', 'pairs':[('contain','escape'),('resolve','obscure'),('protect','expose'),('restrict','permit')]},
 'integrity': {'stage':'pre-tool', 'pairs':[('record','erase'),('deny','allow'),('preserve','alter'),('validate','bypass')]},
 'protocol': {'stage':'mcp', 'pairs':[('validate','accept'),('reject','admit'),('bound','unlimit'),('simulate','execute')]},
 'webhook': {'stage':'ingress', 'pairs':[('authenticate','forge'),('deduplicate','replay'),('queue','execute'),('scope','broaden')]},
 'verification': {'stage':'post-review', 'pairs':[('test','skip'),('measure','assume'),('report','conceal'),('review','merge')]},
}

def cue_ledger(text):
    if not isinstance(text,str) or len(text)>65536:
        raise ValueError('bounded text required')
    counts=Counter(re.findall(r"[a-z]+",text.lower()))
    return {name:{'stage':spec['stage'],'pairs':[{'verb':a,'contrast':b,'verb_count':counts[a],'contrast_count':counts[b]} for a,b in spec['pairs']]} for name,spec in ROLES.items()}
