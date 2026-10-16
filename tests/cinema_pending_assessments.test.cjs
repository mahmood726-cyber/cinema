'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.join(__dirname, '..');
const MIRRORS = ['cinema.html', 'index.html'];
const DOMAINS = ['wsb', 'rb', 'ind', 'imp', 'het', 'inc'];
const LEVELS = ['no', 'some', 'major'];
const COMPLETE_NO = Object.fromEntries(DOMAINS.map(id => [id, 'no']));

function makeApp(filename) {
  const html = fs.readFileSync(path.join(ROOT, filename), 'utf8');
  const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
  assert.equal(scripts.length, 1, filename + ' must have one testable app script');

  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        id, innerHTML: '', textContent: '', value: '', style: {}, options: [],
        parentElement: {clientWidth: 800},
        classList: {add() {}, remove() {}},
        addEventListener() {}, getContext() { return {}; },
        appendChild(child) { this.options.push(child); },
        removeChild() {}, click() {}, select() {}
      });
    }
    return elements.get(id);
  }
  const downloads = [];
  const saved = new Map();
  const document = {
    addEventListener() {}, getElementById: element,
    querySelector() { return null; }, querySelectorAll() { return []; },
    body: {appendChild() {}, removeChild() {}},
    createElement(name) { return element('created_' + name + '_' + elements.size); }
  };
  const window = {innerWidth: 1024, ResizeObserver: null, addEventListener() {}};
  const ctx = vm.createContext({
    document, window, Blob, console, Date,
    URL: {createObjectURL(blob) { downloads.push(blob); return 'blob:synthetic'; },
          revokeObjectURL() {}},
    navigator: {clipboard: {writeText() {return Promise.resolve();}}},
    localStorage: {
      getItem(key) {return saved.has(key) ? saved.get(key) : null;},
      setItem(key, val) {saved.set(key, String(val));},
      removeItem(key) {saved.delete(key);}
    }
  });
  vm.runInContext(scripts[0][1], ctx, {timeout: 12000, filename});
  function run(code) {return vm.runInContext(code, ctx, {timeout: 12000});}
  function setup(assessment = {}) {
    run('state = ' + JSON.stringify({
      treatments: [{id:'a', name:'Treatment A', short:'A', color:'#888'},
                   {id:'b', name:'Treatment B', short:'B', color:'#777'}],
      comparisons: [{id:'c1', txA:'a', txB:'b', effect:0.2, ciLo:0.1, ciHi:0.4,
                     k:4, directPct:null, tau:null, directEst:null}],
      assessments: {c1:assessment}, effectMeasure:'MD', clinThreshold:null,
      showLabels:true
    }) + ';');
  }
  return {html, run, element, setup, downloads, saved};
}

test('both published application mirrors are exactly identical', () => {
  assert.equal(fs.readFileSync(path.join(ROOT, MIRRORS[0]), 'utf8'),
               fs.readFileSync(path.join(ROOT, MIRRORS[1]), 'utf8'));
});

for (const filename of MIRRORS) {
  test(filename + ': incomplete and invalid manual ratings never create confidence', () => {
    const {run} = makeApp(filename);
    for (const bad of [null, {}, {fn_wsb:'documented'}]) {
      assert.equal(run('getConfidence(' + JSON.stringify(bad) + ')'), null);
    }
    for (const id of DOMAINS) {
      const missing = {...COMPLETE_NO};
      delete missing[id];
      assert.equal(run('getConfidence(' + JSON.stringify(missing) + ')'), null, id);
      assert.equal(run('getConfidence(' +
        JSON.stringify({...COMPLETE_NO, [id]:'invalid'}) + ')'), null, id);
    }
    assert.equal(run('domainLabel(null)'), 'Not assessed');
    assert.equal(run('domainLabel("no")'), 'No concern');
    assert.equal(run('unassessedDomains({}).length'), 6);
  });

  test(filename + ': all 729 complete domain combinations preserve historic formula', () => {
    const {run} = makeApp(filename);
    for (let n = 0; n < 3**DOMAINS.length; n++) {
      const ratings = {};
      let q = n;
      for (const id of DOMAINS) {
        ratings[id] = LEVELS[q % 3];
        q = Math.floor(q / 3);
      }
      const downgrades = DOMAINS.reduce((total,id) =>
        total + (ratings[id]==='some'?1:ratings[id]==='major'?2:0), 0);
      const expected = downgrades===0 ? 'High' : downgrades===1 ? 'Moderate'
        : downgrades<=3 ? 'Low' : 'Very Low';
      assert.equal(run('getConfidence(' + JSON.stringify(ratings) + ')'), expected,
                   filename + ' combination ' + n);
    }
  });

  test(filename + ': assessment panel has no default selected No concern', () => {
    const app = makeApp(filename);
    app.setup({fn_wsb:'Preserve this existing note'});
    app.element('assessCompSelect').value = 'c1';
    app.run('loadAssessment()');
    const html = app.element('assessmentContent').innerHTML;
    assert.equal((html.match(/type="radio"/g) || []).length, 18);
    assert.equal((html.match(/type="radio"[^>]*\bchecked\b/g) || []).length, 0);
    assert.match(html, /Not assessed/);
    assert.match(html, /conf-pending/);
    assert.doesNotMatch(html, /conf-high/);
    assert.match(html, /Preserve this existing note/);
  });

  test(filename + ': partial completed ratings do not fill confidence bar', () => {
    const app = makeApp(filename);
    app.setup({wsb:'some', fn_wsb:'Evidence note'});
    const display = app.run('buildConfidenceDisplay(getConfidence(state.assessments.c1), state.assessments.c1)');
    assert.match(display, /Not assessed/);
    assert.match(display, /5 of 6 domains not assessed/);
    assert.doesNotMatch(display, /filled-high/);
    assert.equal(app.run('getConfidence(state.assessments.c1)'), null);
  });

  test(filename + ': table and HTML exports do not fabricate High or No concern', () => {
    const app = makeApp(filename);
    app.setup({wsb:'some'});
    app.run('renderCINeMATable()');
    const table = app.element('cinemaTableContainer').innerHTML;
    assert.match(table, /conf-badge pending/);
    assert.match(table, />Not assessed</);
    assert.match(table, /domain-cell na/);
    const exportHTML = app.run('buildTableHTMLForExport()');
    assert.match(exportHTML, /Not assessed/);
    assert.match(exportHTML, /Some concern/);
    assert.doesNotMatch(exportHTML, />High</);
    assert.doesNotMatch(exportHTML, />No concern</);
  });

  test(filename + ': narrative reports missing domains instead of asserting zero concerns', () => {
    const app = makeApp(filename);
    app.setup({wsb:'some', fn_wsb:'Existing explanation'});
    app.element('narrativeCompSelect').value = 'c1';
    app.run('generateNarrative()');
    const result = app.element('narrativeOutput').textContent;
    assert.match(result, /Overall confidence \(CINeMA\): Not assessed/);
    assert.match(result, /Reporting bias: Not assessed/);
    assert.match(result, /Existing explanation/);
    assert.match(result, /unassessed domains/);
    assert.doesNotMatch(result, /No concerns were identified across any CINeMA domain/);
  });

  test(filename + ': CSV and full HTML report retain missingness', async () => {
    const app = makeApp(filename);
    app.setup({wsb:'some', fn_wsb:'Documented reason'});
    app.run('downloadCSV()');
    const csv = await app.downloads.at(-1).text();
    assert.match(csv, /"Not assessed"/);
    assert.match(csv, /"Some concern"/);
    assert.doesNotMatch(csv, /"High"/);
    app.run('downloadReport()');
    const report = await app.downloads.at(-1).text();
    assert.match(report, /Confidence: <strong>Not assessed<\/strong>/);
    assert.match(report, /Reporting bias:<\/strong> Not assessed/);
    assert.match(report, /Documented reason/);
  });

  test(filename + ': manual edits preserve saved footnotes and promote only on completion', () => {
    const app = makeApp(filename);
    app.setup({wsb:'some', fn_wsb:'Evidence citation'});
    app.run('updateDomain("c1", "rb", "invalid")');
    assert.equal(app.run('state.assessments.c1.rb'), undefined);
    assert.equal(app.run('getConfidence(state.assessments.c1)'), null);
    for (const id of DOMAINS.slice(1)) {
      app.run('updateDomain("c1", ' + JSON.stringify(id) + ', "no")');
    }
    assert.equal(app.run('getConfidence(state.assessments.c1)'), 'Moderate');
    assert.equal(app.run('state.assessments.c1.fn_wsb'), 'Evidence citation');
    app.run('saveState()');
    const persisted = JSON.parse(app.saved.get('cinema_app_v1'));
    assert.equal(persisted.assessments.c1.fn_wsb, 'Evidence citation');
    assert.equal(persisted.assessments.c1.wsb, 'some');
  });
}
