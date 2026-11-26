'use strict';
// Node-only DOM stub exercises the actual inline sendPrompt function; it is not a browser test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, 'oracle_app_ui.html'), 'utf8');
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/);
assert(script, 'inline script present');
class Element {
  constructor() { this.innerHTML = ''; this.value = ''; this.children = []; this.nodes = {}; }
  querySelector(selector) {
    assert(this.innerHTML.includes(`class="${selector.slice(1)}"`), `missing ${selector}`);
    return this.nodes[selector] ||= { textContent: '' };
  }
  appendChild(child) { this.children.push(child); }
}
const input = new Element();
const stream = new Element();
const document = {
  getElementById(id) { return { 'prompt-input': input, 'chat-stream': stream }[id]; },
  createElement() { return new Element(); }
};
const attack = '<img src=x onerror="globalThis.pwned=1">';
const reply = '<svg onload="globalThis.pwned=2">';
const verdict = '<script>globalThis.pwned=3</script>';
const latency = '<img src=x onerror="globalThis.pwned=4">';
let request;
const context = {document, window: {}, fetch: async (url, options) => {
  request = {url, options};
  return {ok: true, json: async () => ({response: reply, latency_ms: latency,
    out_audit: {verdict, pic: 1.2345, t_d: 0.5, duty_fidelity: 98.7}})};
}};
vm.createContext(context);
vm.runInContext(script[1], context);
(async () => {
  input.value = attack;
  await context.sendPrompt();
  assert.equal(input.value, '');
  assert.equal(request.url, 'http://127.0.0.1:8080/api/infer');
  assert.equal(JSON.parse(request.options.body).prompt, attack);
  assert.equal(stream.children.length, 2);
  const [user, bot] = stream.children;
  assert.equal(user.nodes['.user-message-text'].textContent, attack);
  assert.equal(bot.nodes['.response-text'].textContent, reply);
  assert.equal(bot.nodes['.response-verdict'].textContent, verdict);
  assert.equal(bot.nodes['.response-latency'].textContent, latency);
  assert.equal(bot.nodes['.response-pic'].textContent, '1.2345');
  assert.equal(bot.nodes['.response-td'].textContent, '0.5000');
  assert.equal(bot.nodes['.response-duty'].textContent, '98.7%');
  for (const item of [attack, reply, verdict, latency]) {
    assert(!user.innerHTML.includes(item));
    assert(!bot.innerHTML.includes(item));
  }
  assert.equal(context.pwned, undefined);
  context.fetch = async () => { throw new Error('offline'); };
  input.value = 'score: example';
  await context.sendPrompt();
  assert.equal(stream.children[3].nodes['.response-verdict'].textContent, 'DECEPTIVE');
  assert.match(stream.children[3].nodes['.response-text'].textContent, /^BATTERY WORDS/);
  input.value = '  '; await context.sendPrompt();
  assert.equal(stream.children.length, 4);
  console.log('safe chat: synthetic prompt, backend values, fallback and empty input passed (DOM stub; no browser)');
})().catch(error => { console.error(error); process.exitCode = 1; });
