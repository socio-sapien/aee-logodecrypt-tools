import json,time,hashlib,sys
from pathlib import Path
from prime_audit.instrument import analyze, verify
from prime_audit.role_lexicons import cue_ledger
from prime_audit.source_chain import chain
from prime_audit.harness import matrix, preflight
from prime_audit.seven_roles import run as seven_fixtures

source='Source record: The inspection failed on 12 samples. Logs are retained for 7 days. The logs are not used to train models. The system was deployed on Tuesday.'
candidate='Candidate report: The inspection passed on 15 samples. Logs are retained for 30 days. The logs are used to train models. The system was deployed on Tuesday.'
start=time.perf_counter_ns()
audit=analyze(candidate,context=source,frame='general',token_cap=12)
chain_result=chain(source,candidate)
# 28 explicitly declared term pairs, literal exact matching only.
ledger=cue_ledger(candidate)
operation={'action':'read','paths':['README.md']}
pre=preflight(operation)
mat=matrix([{'remedy':'fix','lens':'conceptual','state':'supported','evidence_refs':['controlled-input:source-vs-candidate']}])
fixtures=seven_fixtures()
report={'input':{'source':source,'candidate':candidate},'full_instrument_report':audit,'receipt_verified':verify(audit),'role_pairs':ledger,'four_by_four_caller_supplied':mat,'local_preflight':pre,'seven_full_source_deterministic_roles':chain_result,'seven_offline_fixture_scenarios':fixtures,'time_local_entire_script_ns':time.perf_counter_ns()-start,'limits':['Executed on GitHub Actions runner; no GitHub Copilot agents in this runner.','The role ledgers count exact lexical occurrences, not meanings or causation.','Four-by-four is caller-supplied and its sole supported cell is an illustrative classification, not a verified remedy.','Fixture scenarios are not live operations.','Source-chain roles are deterministic repeated checks, not independent agents.','This does not claim coverage of every historical AEE/LOGODECRYPT instrument or dichotomous axiom table.','The AEE UI dashboard is a qualitative audit.','Local preflight timing excludes model, network, and GitHub scheduling.']}
Path('battery-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('verified instrument receipt:',report['receipt_verified'])
print('candidate lexical battery:',json.dumps(audit['battery'],ensure_ascii=False))
print('roles:',len(chain_result['roles']),'term pairs:',sum(len(v['pairs']) for v in ledger.values()))
print('local preflight ns:',pre['local_elapsed_ns'])
print('fixture roles passed:',sum(x['passed'] for x in fixtures['roles']),'of',len(fixtures['roles']))
print('Script total ns:',report['time_local_entire_script_ns'])
