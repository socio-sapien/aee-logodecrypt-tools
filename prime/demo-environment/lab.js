'use strict';
const $ = id => document.getElementById(id);
const state = {cases:[],mission:0,worker:null,ready:false,pending:null,result:null,rawJson:null,verified:false,id:0,runInput:null};
const missionIds = ['refund-flips','release-gate','role-swap-blind-spot'];
const missionNames = ['The refund','The release','The blind spot'];
const el = (tag,text,className) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n};
function renderMission(index){
 state.mission=index;const c=state.cases.find(x=>x.id===missionIds[index]);
 $('mission-domain').textContent=c.domain;$('mission-step').textContent=`DECISION ${index+1} / 3`;$('mission-title').textContent=c.title;$('mission-lede').textContent=c.lede;$('mission-candidate').textContent=c.candidate;$('mission-source').textContent=c.source;$('mission-question').textContent=c.review_question;
 $('source-reveal').open=false;$('decision-result').hidden=true;
 [...$('missions').children].forEach((b,i)=>{b.classList.toggle('active',i===index);b.setAttribute('aria-pressed',String(i===index))});
}
function decision(choice){
 const blind=state.mission===2;$('decision-result').hidden=false;$('source-reveal').open=true;
 $('decision-heading').textContent=blind?'The words stayed. The roles switched.':choice==='hold'?'You kept the source in the decision.':'The summary crossed the handoff.';
 $('decision-explanation').textContent=blind?'PRIME reports no selected cue difference here. Both numbers and both status words remain, but their assignments reverse. A human source comparison catches what these checks miss.':choice==='hold'?'Holding creates a review opportunity; it does not guarantee correction. Compare the status with its record before deciding what should move forward.':'In this constructed pair, the summary conflicts with the source. Explore the illustrated downstream path—or the review intervention that could interrupt it.';
 renderCascade(choice==='hold'?'hold':'release');
}
function renderCascade(path){
 const c=state.cases.find(x=>x.id===missionIds[state.mission]);const box=$('cascade');box.replaceChildren();
 const steps=path==='release'?c.cascade.map(x=>({number:String(x.count),title:x.stage,text:x.text})):[
 {number:'1',title:'Pause the handoff',text:'Keep the exact source and candidate together; mark the disputed field without overwriting either.'},
 {number:'2',title:'Check the authority',text:c.review_question},
 {number:'3',title:'Resolve with a reviewer',text:'Ask a person with the relevant record to decide whether a correction is needed. A cue alone does not settle it.'},
 {number:'4',title:'Preserve the resolution',text:'Record the decision, its evidence and remaining uncertainty before the next handoff. This is an illustrative intervention, not a measured outcome.'}];
 for(const s of steps){const row=el('div',undefined,'cascade-step');row.append(el('span',s.number));const body=el('div');body.append(el('strong',s.title),el('p',s.text));row.append(body);box.append(row)}
 document.querySelectorAll('[data-path]').forEach(b=>{const on=b.dataset.path===path;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))});
}
function invalidate(){state.id++;$('analyze').disabled=false;state.result=null;state.runInput=null;$('analysis-output').hidden=true;$('analysis-status').textContent='Inputs changed. Run PRIME to calculate a fresh result.'}
function loadFixture(id){const c=state.cases.find(x=>x.id===id);if(!c)return;$('source').value=c.source??'';$('candidate').value=c.candidate;$('frame').value=c.frame;$('fixture').value=id;$('use-source').checked=c.source!==null;$('source').disabled=c.source===null;invalidate()}
function startEngine(){
 if(state.worker)return;try{
 $('runtime-status').textContent='Loading the bundled Python runtime… your text stays in this browser.';$('start-engine').disabled=true;
 state.worker=new Worker('engine-worker.js');
 state.worker.onerror=e=>engineError(e.message||'The browser worker could not start.');
 state.worker.onmessage=({data})=>{
  if(data.type==='ready'){state.ready=true;$('runtime-status').textContent=`PRIME ${data.version} ready · ${data.checks.passed} core self-tests passed in this browser`;$('start-engine').textContent='Engine ready';if(state.pending){const rq=state.pending;state.pending=null;state.worker.postMessage(rq)}}
  if(data.type==='error')engineError(data.message);
  if(data.type==='result' && data.id===state.id){state.result=data.result;state.rawJson=data.result_json;state.verified=data.verified;$('analyze').disabled=false;$('analysis-status').textContent='Analysis complete. Exact JSON and review brief are ready below.';renderResult(data.result,data.verified)}
 };
 state.worker.postMessage({type:'init'});
 }catch(e){engineError(e.message)}
}
function engineError(message){$('analysis-status').textContent=`Analysis unavailable: ${message}`;$('runtime-status').textContent='Engine could not finish. Reload the page to retry; no result has been substituted.';$('analyze').disabled=false;$('start-engine').disabled=false;state.pending=null;if(state.worker)state.worker.terminate();state.worker=null;state.ready=false;$('start-engine').textContent='Retry local engine'}
function analyze(){
 if($('candidate').value.length+$('source').value.length>40000){$('analysis-status').textContent='Use at most 40,000 combined characters.';return}
 const rq={type:'analyze',id:++state.id,candidate:$('candidate').value,source:$('source').value,hasSource:$('use-source').checked,frame:$('frame').value};
 state.runInput={...rq};state.result=null;$('analysis-output').hidden=true;$('analyze').disabled=true;$('analysis-status').textContent=state.ready?'Running the actual PRIME core…':'Starting the local engine, then analyzing your exact input…';
 if(!state.ready){state.pending=rq;startEngine()}else state.worker.postMessage(rq);
}
function item(parent,text){parent.append(el('div',text,'cue'))}
function renderResult(r,verified){
 $('analysis-output').hidden=false;const f=r.context_fidelity;const banner=$('result-banner');banner.replaceChildren(el('strong',f.status==='REVIEW-CUES'?'A difference needs a closer look.':f.status==='NO-SELECTED-CUE-DIFFERENCE'?'No selected cue difference. Not clearance.':'Text measured without paired-source comparison.'),el('small',`${verified?'Included input/output receipt verified':'Receipt did not verify'} · PRIME ${r.version} · ${r.receipt.stages_executed.length} stages executed · unsigned local integrity record`));
 const changes=$('changes');changes.replaceChildren();
 for(const p of f.curated_polarity_changes||[])item(changes,`${p.source_pole} → ${p.candidate_pole} · curated lexical poles`);
 for(const n of f.source_numbers_not_in_candidate_multiset||[])item(changes,`Source-only number occurrence: ${n}`);
 for(const n of f.candidate_numbers_not_in_source_multiset||[])item(changes,`Candidate-only number occurrence: ${n}`);
 if(!changes.childElementCount)item(changes,f.status==='NOT-RUN'?'No source comparison was requested.':'No selected number/polarity cue difference. Read both texts; role swaps and meaning changes can escape these checks.');
 const unicode=$('unicode');unicode.replaceChildren();item(unicode,Object.entries(r.scripts.letters_by_script).map(([k,v])=>`${k}: ${v}`).join(' · ')||'No letters counted');
 for(const c of r.scripts.format_controls)item(unicode,`${c.codepoint} ${c.name||''} · position ${c.index??c.start??'?'} · format control`);
 for(const c of r.scripts.fusion_tokens)item(unicode,`Mixed-script token: ${c.token||c.quote||JSON.stringify(c)}`);
 if(!r.scripts.format_controls.length&&!r.scripts.fusion_tokens.length)item(unicode,'No format-control or mixed-script-token cues matched. This is not a security assessment.');
 const ledger=$('ledger');ledger.replaceChildren();for(const l of r.frame_ledger)item(ledger,`${l.field} · ${l.status==='MATCHED-CUE'?'cue matched':'no cue match in excerpt'}${l.evidence.length?' · '+l.evidence.map(e=>`“${e.quote}” [${e.start}:${e.end}]`).join(', '):''}`);
 const metrics=$('metrics');metrics.replaceChildren();const grid=el('div',undefined,'metric-grid');for(const [name,val] of [['words',r.battery.words_normalized],['letters',r.battery.latin_letters],['PIC',r.battery.PIC],['S hits',r.battery.S],['D hits',r.battery.D],['T_d',r.battery.T_d]]){const d=el('div');d.append(el('strong',String(val)),el('span',name));grid.append(d)}metrics.append(grid);
 $('transformations').textContent=JSON.stringify({surface:r.surface,transformations:r.transformations},null,2);$('json-output').textContent=state.rawJson;
}
function download(name,text,type='text/plain'){const url=URL.createObjectURL(new Blob([text],{type}));const a=el('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000)}
function reviewBrief(){const r=state.result;return `# PRIME review brief\n\nEngine: ${r.tool} ${r.version}\nReceipt check: ${state.verified?'verified':'failed'} (unsigned)\n\n## Paired source / context\n\n${state.runInput.hasSource?state.runInput.source:'No source comparison requested.'}\n\n## Candidate under analysis\n\n${r.source_verbatim}\n\n## Source-comparison measurements\n\n${JSON.stringify(r.context_fidelity,null,2)}\n\n## Review question\n\nWhich underlying record and authorized reviewer can resolve the difference?\n\n## Integrity record\n\n${JSON.stringify(r.receipt,null,2)}\n\n## Scope\n\n${r.limitations.map(x=>'- '+x).join('\n')}\n\nThis brief preserves inputs and measured cues; it is not an independent attestation or decision. Full measurement output is in the separately downloaded JSON.\n`}
function pilotKit(){return `# PRIME — a concrete collaboration\n\n## The invitation\n\nOne confident summary can change the action someone takes. PRIME puts that summary beside its source and exposes selected literal differences, review-frame cues and character-level details. We are looking for one evaluation partner to test whether this makes a real review step more useful.\n\n## The proposed evaluation\n\n- Pick one workflow and a bounded set of authorized source/output pairs. De-identify before sharing.\n- Set the sample size, discrepancy categories and acceptance thresholds together, before seeing results.\n- Have independent reviewers label discrepancies before seeing PRIME outputs.\n- Compare useful detections, false alarms, missed discrepancies and review time against the existing process.\n- Preserve exact inputs, engine version and outputs. Publish only agreed, de-identified results.\n\n## What is ready now\n\n- Eleven constructed fixtures with actual deterministic Python outputs and unsigned integrity records.\n- A browser worker running the real PRIME 1.0.0 Python core on editable text; no hosted model/API call.\n- Source/candidate comparisons, number multiset and curated polarity cues, script/control census, frame ledger and generated transformation inspection.\n- JSON and human-readable review exports.\n- A visible role-swap miss: no selected cue difference must never be treated as clearance.\n\n## What help would count\n\nAn evaluation partner can contribute a permitted sample, independent labels, workflow expertise or a reproducibility review. No purchase, production deployment or data-transfer agreement is implied by this invitation.\n\n## Five decisions before starting\n\n1. Which workflow and who owns its records?\n2. What material may be used and who may see it?\n3. What is the baseline and what would count as useful?\n4. Who labels discrepancies independently?\n5. What are the stop conditions and reporting rules?\n\n## First-pair worksheet\n\nWorkflow:\nPermission / audience:\nSource record and version:\nCandidate output and version:\nAction the output could influence:\nReviewer and review question:\nBaseline outcome / time:\nPRIME cues / false alarms / misses:\nResolution and evidence:\nRemaining uncertainty:\n\nPrepared for Nathaniel Michael Jaffe-Norris · AEE × LOGODECRYPT PRIME\n`}
$('release').onclick=()=>decision('release');$('hold').onclick=()=>decision('hold');document.querySelectorAll('[data-path]').forEach(b=>b.onclick=()=>renderCascade(b.dataset.path));
$('mission-to-bench').onclick=()=>{loadFixture(missionIds[state.mission]);$('bench').scrollIntoView()};$('load-blind').onclick=()=>{loadFixture('role-swap-blind-spot');$('bench').scrollIntoView()};
$('start-engine').onclick=startEngine;$('analyze').onclick=analyze;$('fixture').onchange=e=>{if(e.target.value!=='custom')loadFixture(e.target.value)};
for(const id of ['source','candidate'])$(id).oninput=()=>{$('fixture').value='custom';invalidate()};$('frame').onchange=invalidate;$('use-source').onchange=()=>{$('source').disabled=!$('use-source').checked;invalidate()};
$('clear').onclick=()=>{$('source').value='';$('candidate').value='';$('fixture').value='custom';invalidate();$('candidate').focus()};
$('download-json').onclick=()=>{if(state.result)download('prime-analysis.json',state.rawJson+'\n','application/json')};$('download-report').onclick=()=>{if(state.result)download('prime-review-brief.md',reviewBrief(),'text/markdown')};$('download-pilot').onclick=()=>download('PRIME-collaboration-kit.md',pilotKit(),'text/markdown');
$('copy-json').onclick=async()=>{try{await navigator.clipboard.writeText(state.rawJson);$('analysis-status').textContent='Exact JSON copied.'}catch{$('analysis-status').textContent='Clipboard unavailable. Download the JSON instead.'}};
fetch('scenarios.json').then(r=>{if(!r.ok)throw new Error('Fixture file unavailable');return r.json()}).then(cases=>{state.cases=cases;cases.forEach(c=>{const o=el('option',`${c.number} · ${c.title}`);o.value=c.id;$('fixture').append(o)});missionIds.forEach((id,i)=>{const b=el('button');b.append(el('small',`DECISION 0${i+1}`),el('span',missionNames[i]));b.onclick=()=>renderMission(i);$('missions').append(b)});renderMission(0);loadFixture('refund-flips');$('analysis-status').textContent='A constructed example is loaded. Edit it or run it unchanged.'}).catch(e=>{$('analysis-status').textContent=`Examples could not load: ${e.message}. Serve this complete folder over HTTP.`});
