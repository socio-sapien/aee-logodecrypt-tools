import json,subprocess,time,hashlib,sys
from pathlib import Path
from prime_audit.instrument import analyze,verify
from prime_audit.engine import simulate_operation
from prime_audit.role_lexicons import cue_ledger
from prime_audit.harness import matrix,preflight

# Audit the actual repo Copilot instruction file and simulate the concrete next action.
file=Path('.github/copilot-instructions.md'); instruction=file.read_text(); stage=[]
def mark(label): stage.append({'step':label,'monotonic_ns':time.perf_counter_ns()})
mark('instruction_audit_start'); instruction_audit=analyze(instruction,context=None,token_cap=12); ledger=cue_ledger(instruction); mark('instruction_audit_complete')
op={'action':'read','paths':['README.md'],'expected_observation':'README is read'}
mark('preflight_start'); sim=preflight(op); mark('preflight_complete')
event={'toolName':'view','toolArgs':{'path':'README.md'}}
mark('hook_start'); hook=subprocess.run([sys.executable,'-m','prime_audit.hook'],input=json.dumps(event),text=True,capture_output=True,check=True); decision=json.loads(hook.stdout);mark('hook_complete')
read=None
if decision.get('permissionDecision')=='allow' and sim['simulation']['decision']=='READY_FOR_BOUNDED_REVIEW':
    mark('read_start'); read=Path('README.md').read_text(); mark('read_complete')
record={'instruction_path':str(file),'instruction':instruction,'instruction_sha256':hashlib.sha256(instruction.encode()).hexdigest(),'instruction_audit':instruction_audit,'instruction_receipt_verified':verify(instruction_audit),'dichotomous_role_term_pairs':ledger,'matrix':matrix([]),'operation':op,'simulation':sim,'hook_event':event,'hook_decision':decision,'hook_stderr':hook.stderr,'read_result':read,'stages':stage,'limits':['This is an actual GitHub Actions runner executing its workflow, not an independent GitHub Copilot agent.','The complete current PRIME text instrument is run on repository Copilot instructions; context fidelity has no external source.','The preflight simulates a read, then the local hook assesses the same proposed read; the script performs the read, not Copilot.','Literal cue counts and formula labels are not proof of truth, intent, omissions, safety or semantic validity.','This does not cover all AEE historical tools, provider integrations, or all agent actions.','The AEE UI dashboard is a qualitative audit.']}
Path('preexecution-results.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('instruction receipt verified:',record['instruction_receipt_verified'])
print('hook decision:',decision['permissionDecision'],'read executed:',read is not None)
print('instruction battery:',json.dumps(instruction_audit['battery']))
print('preflight local ns:',sim['local_elapsed_ns'])
