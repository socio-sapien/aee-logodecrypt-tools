/* PRIME browser bridge. All computation stays in this worker. */
let engine;
async function boot() {
  importScripts('runtime/pyodide.js');
  const py = await loadPyodide({indexURL: new URL('runtime/', self.location.href).href});
  const response = await fetch('../aee_logodecrypt_prime.py');
  if (!response.ok) throw new Error('PRIME source could not be loaded. Serve the complete package over HTTP.');
  const source = await response.text();
  py.runPython("import types, json\nprime = types.ModuleType('prime_browser')");
  py.globals.set('prime_source', source);
  py.runPython("exec(prime_source, prime.__dict__)");
  const checks = JSON.parse(py.runPython('json.dumps(prime.self_test())'));
  self.postMessage({type:'ready', version:py.runPython('prime.VERSION'), checks});
  return py;
}
self.onmessage = async ({data}) => {
  try {
    engine ||= boot();
    const py = await engine;
    if (data.type === 'init') return;
    if (data.type !== 'analyze') throw new Error('Unknown request');
    if (typeof data.candidate !== 'string' || typeof data.source !== 'string' || data.candidate.length + data.source.length > 40000) throw new Error('Use at most 40,000 combined characters.');
    py.globals.set('request_json', JSON.stringify(data));
    const payload = py.runPython(`
rq = json.loads(request_json)
result = prime.analyze(rq['candidate'], rq['source'] if rq['hasSource'] else None, rq['frame'], 12)
json.dumps({'result':result,'result_json':json.dumps(result,ensure_ascii=False,indent=2),'verified':prime.verify(result)}, ensure_ascii=False)
`);
    self.postMessage({type:'result', id:data.id, ...JSON.parse(payload)});
  } catch(error) { self.postMessage({type:'error', id:data.id, message:String(error.message || error)}); }
};
