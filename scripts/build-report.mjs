#!/usr/bin/env node
// Builds report.html from the eval runs: accuracy, time and credit used for
// each memory setup, for every task suite that has results.
//
//   node scripts/build-report.mjs            writes report.html
//
// Reads .dream-state/evals/runs*.jsonl (written by scripts/run-evals.sh), so
// rerun it whenever more runs finish. The page is one self-contained file.
import fs from "node:fs";
import path from "node:path";

const RUNS_DIR = ".dream-state/evals";
const WORK = process.env.EVAL_WORK || path.join("..", "dream-lab-evals");
const OUT = process.argv[2] || "report.html";

const SETUPS = [
  { id: "none", name: "No memory", note: "Only the code. No memory folder, no memory rules." },
  { id: "memory", name: "Memory", note: "Notes from the learning tasks, never sorted." },
  { id: "dreaming", name: "Memory + dreaming", note: "The same notes after one dreaming pass." },
];
const SUITES = {
  easy: { title: "Easy tasks", tasks: "tasks/tasks.json", work: WORK,
          about: "One-line bugs with a failing test that points at them. Scored on that test." },
  hard: { title: "Hard tasks", tasks: "tasks-hard/tasks.json", work: path.join(WORK, "hard"),
          about: "Whole features, scored on hidden tests. The similar tasks need store rules that only the learning tasks explain." },
  veryhard: { title: "Very hard tasks", tasks: "tasks-veryhard/tasks.json", work: path.join(WORK, "veryhard"),
          about: "Scored on hidden tests. The rules come only as failing tests, one rule changes halfway, and each similar task needs several rules at once." },
};
const GROUPS = ["similar", "new", "different"];
const GROUP_NOTE = { similar: "repeats what the learning tasks taught", new: "new problem, same codebase", different: "unrelated code" };

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const avg = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
const sum = (xs) => xs.reduce((a, b) => a + b, 0);
const fmtTime = (s) => { s = Math.round(s); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
  return h ? `${h}h ${m}m` : m ? `${m}m ${String(s % 60).padStart(2, "0")}s` : `${s}s`; };
const fmtTokens = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(2)}M` : n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${Math.round(n)}`);
const fmtCost = (n) => `$${n.toFixed(2)}`;
const fmtPct = (n) => `${Math.round(n * 100)}%`;
const readJson = (f) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return null; } };

function readRuns(file) {
  const last = new Map();                        // a rerun replaces the earlier row
  for (const line of fs.readFileSync(file, "utf8").split("\n").filter(Boolean)) {
    const r = JSON.parse(line);
    last.set(`${r.setup}|${r.task}|${r.repeat}`, r);
  }
  return [...last.values()];
}

function stats(rs) {
  const hidden = rs.filter((r) => r.hidden_total > 0);
  return {
    runs: rs.length, passed: rs.filter((r) => r.passed).length,
    accuracy: rs.length ? rs.filter((r) => r.passed).length / rs.length : null,
    hidden: hidden.length ? avg(hidden.map((r) => r.hidden_passed / r.hidden_total)) : null,
    seconds: avg(rs.map((r) => r.seconds)), tokens: avg(rs.map((r) => r.tokens)), cost: avg(rs.map((r) => r.cost_usd)),
    turns: avg(rs.map((r) => r.turns)),
    totalSeconds: sum(rs.map((r) => r.seconds)), totalTokens: sum(rs.map((r) => r.tokens)), totalCost: sum(rs.map((r) => r.cost_usd)),
  };
}

// One metric: a horizontal bar per setup, on one shared scale.
function chart(title, sub, rows, max) {
  const bars = rows.map(({ setup, value, label, tip }) => {
    if (value === null) return `<div class="row"><span class="who">${esc(setup.name)}</span><span class="track"></span><span class="val muted">not run</span></div>`;
    const width = max > 0 ? Math.max((value / max) * 100, value > 0 ? 0.8 : 0) : 0;
    return `<div class="row" tabindex="0" data-tip="${esc(tip)}"><span class="who">${esc(setup.name)}</span>` +
      `<span class="track"><span class="bar s-${setup.id}" style="width:${width.toFixed(2)}%"></span></span>` +
      `<span class="val">${esc(label)}</span></div>`;
  }).join("");
  return `<figure class="chart"><figcaption><strong>${esc(title)}</strong><span>${esc(sub)}</span></figcaption>${bars}</figure>`;
}

function suiteSection(key, runs, label) {
  const meta = SUITES[key] || { title: `${key} tasks`, tasks: null, work: path.join(WORK, key), about: "" };
  const taskList = meta.tasks ? readJson(meta.tasks)?.tasks ?? [] : [];
  const evalTasks = taskList.filter((t) => t.group !== "learn").length;
  const evalRuns = runs.filter((r) => r.setup !== "learning");
  const repeats = Math.max(1, ...evalRuns.map((r) => r.repeat));
  const expected = evalTasks * repeats;
  const by = Object.fromEntries(SETUPS.map((s) => [s.id, stats(evalRuns.filter((r) => r.setup === s.id))]));
  const has = (id) => by[id].runs > 0;
  const hasHidden = evalRuns.some((r) => r.hidden_total > 0);

  const rows = (pick, fmt, tipFn) => SETUPS.map((s) => ({
    setup: s, value: has(s.id) ? pick(by[s.id]) : null,
    label: has(s.id) ? fmt(pick(by[s.id])) : "", tip: has(s.id) ? tipFn(by[s.id], s) : "" }));
  const max = (pick) => Math.max(0, ...SETUPS.filter((s) => has(s.id)).map((s) => pick(by[s.id])));
  const runsNote = (st) => `${st.runs} run${st.runs === 1 ? "" : "s"}`;

  const charts = [
    chart("Accuracy", hasHidden ? "runs that passed the visible and every hidden test" : "runs that passed the task's test",
      rows((s) => s.accuracy, fmtPct, (st, s) => `${s.name}: ${st.passed} of ${st.runs} runs passed`), 1),
    chart("Time per task", "average, from prompt to finished",
      rows((s) => s.seconds, fmtTime, (st, s) => `${s.name}: ${fmtTime(st.seconds)} on average, ${fmtTime(st.totalSeconds)} in total over ${runsNote(st)}`), max((s) => s.seconds)),
    chart("Credit per task", "average tokens used",
      rows((s) => s.tokens, fmtTokens, (st, s) => `${s.name}: ${fmtTokens(st.tokens)} tokens on average, ${fmtTokens(st.totalTokens)} in total over ${runsNote(st)}`), max((s) => s.tokens)),
    chart("Cost per task", "average, at API list prices",
      rows((s) => s.cost, fmtCost, (st, s) => `${s.name}: ${fmtCost(st.cost)} on average, ${fmtCost(st.totalCost)} in total over ${runsNote(st)}`), max((s) => s.cost)),
  ];
  if (hasHidden) charts.splice(1, 0, chart("Hidden tests passed", "average share per run (partial credit)",
    rows((s) => s.hidden, fmtPct, (st, s) => `${s.name}: ${fmtPct(st.hidden ?? 0)} of hidden tests passed on average`), 1));

  // Completeness: say plainly when a setup isn't finished.
  const progress = SETUPS.map((s) => {
    const st = by[s.id];
    const state = !st.runs ? "not run yet" : expected && st.runs < expected ? `${st.runs} of ${expected} runs done` : `${st.runs} runs`;
    const cls = !st.runs || (expected && st.runs < expected) ? "partial" : "";
    return `<li class="${cls}"><span class="swatch s-${s.id}"></span><span><strong>${esc(s.name)}</strong> ${esc(s.note)} <em>${esc(state)}</em></span></li>`;
  }).join("");

  // Table: every number behind the charts, split by task group.
  const cell = (st) => (st.runs ? `${st.passed}/${st.runs}` : "–");
  const groupRows = GROUPS.map((g) => {
    const cells = SETUPS.map((s) => {
      const st = stats(evalRuns.filter((r) => r.setup === s.id && r.group === g));
      const extra = st.runs ? `<small>${fmtTime(st.seconds)} · ${fmtTokens(st.tokens)}${st.hidden !== null ? ` · hidden ${fmtPct(st.hidden)}` : ""}</small>` : "";
      return `<td>${cell(st)}${extra}</td>`;
    }).join("");
    return `<tr><th scope="row">${g}<small>${GROUP_NOTE[g]}</small></th>${cells}</tr>`;
  }).join("");
  const totalRow = `<tr class="total"><th scope="row">All tasks<small>totals for the whole setup</small></th>${SETUPS.map((s) => {
    const st = by[s.id];
    return `<td>${cell(st)}${st.runs ? `<small>${fmtTime(st.totalSeconds)} · ${fmtTokens(st.totalTokens)} · ${fmtCost(st.totalCost)}</small>` : ""}</td>`;
  }).join("")}</tr>`;

  // One-off costs that the memory setups pay before any eval task.
  const learning = stats(runs.filter((r) => r.setup === "learning"));
  const work = label ? path.join(WORK, "models", label, path.relative(WORK, meta.work)) : meta.work;
  const dream = readJson(path.join(work, "state", "dream.json"));
  const extras = [];
  if (learning.runs) extras.push(`<li><strong>Learning tasks</strong> (both memory setups): ${learning.passed}/${learning.runs} passed, ${fmtTime(learning.totalSeconds)}, ${fmtTokens(learning.totalTokens)} tokens, ${fmtCost(learning.totalCost)}.</li>`);
  if (dream) extras.push(`<li><strong>Dreaming pass</strong> (memory + dreaming only): ${fmtTokens(dream.tokens)} tokens, ${fmtCost(dream.cost_usd)}. Memory went from ${dream.memory_tokens_before} to ${dream.memory_tokens_after} tokens, and the judge scored it ${dream.judge_score ?? "–"}/5.</li>`);

  return `<section>
  <h2>${esc(meta.title)}${label ? ` · ${esc(label)}` : ""}</h2>
  <p class="about">${esc(meta.about)} ${evalTasks ? `${evalTasks} tasks, ${repeats} run${repeats === 1 ? "" : "s"} each per setup.` : ""}</p>
  <ul class="legend">${progress}</ul>
  <div class="charts">${charts.join("")}</div>
  <div class="tablewrap"><table>
    <thead><tr><th scope="col">Task group</th>${SETUPS.map((s) => `<th scope="col"><span class="swatch s-${s.id}"></span>${esc(s.name)}</th>`).join("")}</tr></thead>
    <tbody>${groupRows}${totalRow}</tbody>
  </table></div>
  <p class="tablenote">Each cell: runs passed out of runs done, then average time and tokens per task.</p>
  ${extras.length ? `<h3>One-off costs</h3><ul class="extras">${extras.join("")}</ul>` : ""}
</section>`;
}

// ---- Rounds experiment: every setup does all the tasks, round after round. ----
function niceMax(v) {
  if (v <= 0) return 1;
  const p = 10 ** Math.floor(Math.log10(v));
  return [1, 2, 2.5, 5, 10].map((m) => m * p).find((m) => m >= v);
}

// One metric over the rounds: a line per setup on one shared scale.
function lineChart(title, sub, series, rounds, fmt, fixedMax) {
  const W = 440, H = 210, L = 52, R = 14, T = 12, B = 34;
  const all = series.flatMap((s) => s.points.map((p) => p.value));
  const top = fixedMax ?? niceMax(Math.max(0, ...all));
  const x = (r) => (rounds === 1 ? L + (W - L - R) / 2 : L + ((r - 1) / (rounds - 1)) * (W - L - R));
  const y = (v) => T + (1 - v / top) * (H - T - B);
  const grid = [0, 0.5, 1].map((f) => `<line class="grid" x1="${L}" x2="${W - R}" y1="${y(top * f).toFixed(1)}" y2="${y(top * f).toFixed(1)}"/>` +
    `<text class="tick" x="${L - 8}" y="${(y(top * f) + 4).toFixed(1)}" text-anchor="end">${esc(fmt(top * f))}</text>`).join("");
  const xs = Array.from({ length: rounds }, (_, i) => `<text class="tick" x="${x(i + 1).toFixed(1)}" y="${H - B + 16}" text-anchor="middle">${i + 1}</text>`).join("");
  const lines = series.map((s) => {
    if (!s.points.length) return "";
    const path = s.points.map((p, i) => `${i ? "L" : "M"}${x(p.round).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
    const dots = s.points.map((p) => `<circle class="dot f-${s.id}" cx="${x(p.round).toFixed(1)}" cy="${y(p.value).toFixed(1)}" r="4"/>` +
      `<circle class="hit" tabindex="0" cx="${x(p.round).toFixed(1)}" cy="${y(p.value).toFixed(1)}" r="11" data-tip="${esc(`${s.name}, round ${p.round}: ${p.tip}`)}"/>`).join("");
    return `<path class="line l-${s.id}" d="${path}"/>${dots}`;
  }).join("");
  return `<figure class="chart"><figcaption><strong>${esc(title)}</strong><span>${esc(sub)}</span></figcaption>` +
    `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(title)} by round">${grid}${xs}` +
    `<text class="tick" x="${(L + W - R) / 2}" y="${H - 2}" text-anchor="middle">Round</text>${lines}</svg></figure>`;
}

function roundsSection(key, runs, extra, label) {
  const meta = SUITES[key] || { title: `${key} tasks`, tasks: null, about: "" };
  const taskCount = meta.tasks ? (readJson(meta.tasks)?.tasks ?? []).length : new Set(runs.map((r) => r.task)).size;
  const rounds = Math.max(1, ...runs.map((r) => r.repeat));
  const at = (setup, round) => stats(runs.filter((r) => r.setup === setup && r.repeat === round));
  const hasHidden = runs.some((r) => r.hidden_total > 0);
  const series = (pick, tip) => SETUPS.map((s) => ({ ...s, points: Array.from({ length: rounds }, (_, i) => i + 1)
    .map((round) => ({ round, st: at(s.id, round) })).filter((p) => p.st.runs)
    .map((p) => ({ round: p.round, value: pick(p.st), tip: tip(p.st) })) }));
  const memory = SETUPS.map((s) => ({ ...s, points: extra.filter((e) => e.kind === "memory" && e.setup === s.id)
    .map((e) => ({ round: e.round, value: e.memory_tokens, tip: `${e.memory_tokens} tokens of memory at the end of the round` })) }));

  const charts = [
    lineChart("Accuracy", hasHidden ? "runs that passed the visible and every hidden test" : "runs that passed the task's test",
      series((st) => st.accuracy * 100, (st) => `${st.passed} of ${st.runs} runs passed`), rounds, (v) => `${Math.round(v)}%`, 100),
    lineChart("Time per task", "average, from prompt to finished",
      series((st) => st.seconds, (st) => `${fmtTime(st.seconds)} per task, ${fmtTime(st.totalSeconds)} for the round`), rounds, fmtTime),
    lineChart("Credit per task", "average tokens used",
      series((st) => st.tokens, (st) => `${fmtTokens(st.tokens)} tokens per task, ${fmtTokens(st.totalTokens)} for the round (${fmtCost(st.totalCost)})`), rounds, fmtTokens),
  ];
  if (memory.some((m) => m.points.length)) charts.push(lineChart("Memory size", "tokens in the memory folder at the end of each round", memory, rounds, fmtTokens));

  const progress = SETUPS.map((s) => {
    const done = Array.from({ length: rounds }, (_, i) => at(s.id, i + 1).runs).filter((n) => n >= taskCount).length;
    const any = runs.some((r) => r.setup === s.id);
    const state = !any ? "not run yet" : done < rounds ? `${done} of ${rounds} rounds done` : `${rounds} rounds`;
    return `<li class="${!any || done < rounds ? "partial" : ""}"><span class="swatch s-${s.id}"></span><span><strong>${esc(s.name)}</strong> ${esc(s.note.replace("from the learning tasks, never sorted", "kept from task to task and round to round, never sorted").replace("The same notes after one dreaming pass", "The same, with a dreaming pass after every round"))} <em>${esc(state)}</em></span></li>`;
  }).join("");

  const rows = Array.from({ length: rounds }, (_, i) => i + 1).map((round) => {
    const cells = SETUPS.map((s) => {
      const st = at(s.id, round);
      if (!st.runs) return "<td>–</td>";
      const part = st.runs < taskCount ? ` <em class="part">(${st.runs} of ${taskCount} tasks)</em>` : "";
      return `<td>${st.passed}/${st.runs} passed${part}<small>${fmtTime(st.totalSeconds)} · ${fmtTokens(st.totalTokens)} · ${fmtCost(st.totalCost)}</small></td>`;
    }).join("");
    const d = extra.find((e) => e.kind === "dream" && e.round === round);
    const dream = d ? `<td>${fmtTokens(d.tokens)} · ${fmtCost(d.cost_usd)}<small>${fmtTime(d.seconds)} · memory ${d.memory_before} to ${d.memory_after} tokens · judge ${d.judge_score ?? "–"}/5</small></td>` : "<td>–</td>";
    return `<tr><th scope="row">Round ${round}</th>${cells}${dream}</tr>`;
  }).join("");
  const totals = `<tr class="total"><th scope="row">All rounds</th>${SETUPS.map((s) => {
    const st = stats(runs.filter((r) => r.setup === s.id));
    return st.runs ? `<td>${st.passed}/${st.runs} passed<small>${fmtTime(st.totalSeconds)} · ${fmtTokens(st.totalTokens)} · ${fmtCost(st.totalCost)}</small></td>` : "<td>–</td>";
  }).join("")}${(() => { const ds = extra.filter((e) => e.kind === "dream");
    return ds.length ? `<td>${fmtTokens(sum(ds.map((d) => d.tokens)))} · ${fmtCost(sum(ds.map((d) => d.cost_usd)))}<small>${ds.length} dreaming pass${ds.length === 1 ? "" : "es"}</small></td>` : "<td>–</td>"; })()}</tr>`;

  return `<section>
  <h2>${esc(meta.title)}, round by round${label ? ` · ${esc(label)}` : ""}</h2>
  <p class="about">Every setup does all ${taskCount} tasks, then does them again. Memory carries over from task to task and round to round; without memory every round starts from nothing. ${esc(meta.about)}</p>
  <ul class="legend">${progress}</ul>
  <div class="charts">${charts.join("")}</div>
  <div class="tablewrap"><table class="rounds">
    <thead><tr><th scope="col">What each round used</th>${SETUPS.map((s) => `<th scope="col"><span class="swatch s-${s.id}"></span>${esc(s.name)}</th>`).join("")}<th scope="col">Dreaming pass after it</th></tr></thead>
    <tbody>${rows}${totals}</tbody>
  </table></div>
  <p class="tablenote">Each cell: runs passed, then the round's total time, tokens and cost. The dreaming pass is extra, on top of the memory + dreaming column.</p>
</section>`;
}

// Runs on the default model are in RUNS_DIR; runs on another model (run-evals.sh
// --model) are in RUNS_DIR/models/<model>/ and get their own sections.
const order = Object.keys(SUITES);
const readExtra = (f) => (fs.existsSync(f) ? fs.readFileSync(f, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)) : []);
function load(dir, label) {
  const names = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
  const suites = names.filter((f) => /^runs(-[\w-]+)?\.jsonl$/.test(f))
    .map((f) => ({ key: f === "runs.jsonl" ? "easy" : f.slice(5, -6), label, runs: readRuns(path.join(dir, f)) }));
  const rounds = names.filter((f) => /^rounds-[\w]+\.jsonl$/.test(f))
    .map((f) => { const key = f.slice(7, -6);
      return { key, label, runs: readRuns(path.join(dir, f)), extra: readExtra(path.join(dir, `rounds-${key}-extra.jsonl`)) }; });
  return { suites, rounds };
}
const modelDirs = fs.existsSync(path.join(RUNS_DIR, "models")) ? fs.readdirSync(path.join(RUNS_DIR, "models")).filter((m) => /^[\w.-]+$/.test(m)).sort() : [];
const loaded = [load(RUNS_DIR, null), ...modelDirs.map((m) => load(path.join(RUNS_DIR, "models", m), m))];
const bySuite = (a, b) => order.indexOf(a.key) - order.indexOf(b.key);
// Same task set together, default model first, then the others.
const suites = loaded.flatMap((l) => l.suites).sort(bySuite);
const roundSuites = loaded.flatMap((l) => l.rounds).sort(bySuite);
if (!suites.length && !roundSuites.length) { console.error(`No runs found in ${RUNS_DIR}. Run scripts/run-evals.sh first.`); process.exit(1); }
const model = readJson(path.join(process.env.PI_CODING_AGENT_DIR || path.join(process.env.HOME || process.env.USERPROFILE || "", ".pi", "agent"), "settings.json"))?.defaultModel;
const today = new Date().toISOString().slice(0, 10);

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>dream-lab results</title>
<style>
/* Layout: one column; each suite is a legend, a row of small bar charts on shared setup colors, then the table behind them. */
:root {
  --bg: #fcfcfb; --panel: #f4f3f0; --line: #e3e1db; --fg: #0b0b0b; --fg2: #52514e; --muted: #7a7872; --warn: #8a5a00;
  --s-none: #2a78d6; --s-memory: #eb6834; --s-dreaming: #1baf7a;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #1a1a19; --panel: #242422; --line: #383835; --fg: #f0efec; --fg2: #c3c2b7; --muted: #96958d; --warn: #e0b055;
  --s-none: #3987e5; --s-memory: #d95926; --s-dreaming: #199e70; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #1a1a19; --panel: #242422; --line: #383835; --fg: #f0efec; --fg2: #c3c2b7; --muted: #96958d; --warn: #e0b055;
  --s-none: #3987e5; --s-memory: #d95926; --s-dreaming: #199e70; color-scheme: dark }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 var(--font); }
main { max-width: 1040px; margin: 0 auto; padding-block: 32px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 40px; }
h1 { font-size: 28px; line-height: 1.2; margin: 0 0 6px; text-wrap: balance; }
h2 { font-size: 20px; margin: 0 0 4px; }
h3 { font-size: 14px; margin: 20px 0 6px; }
p { margin: 0; }
.lede, .about { color: var(--fg2); max-width: 70ch; }
section { display: grid; gap: 14px; border-top: 1px solid var(--line); padding-top: 24px; }
.swatch { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 8px; flex: none; }
.s-none { background: var(--s-none); } .s-memory { background: var(--s-memory); } .s-dreaming { background: var(--s-dreaming); }
.legend { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; color: var(--fg2); font-size: 14px; }
.legend li { display: flex; align-items: baseline; }
.legend strong { color: var(--fg); }
.legend em { font-style: normal; color: var(--muted); margin-left: 4px; }
.legend .partial em { color: var(--warn); font-weight: 600; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 400px), 1fr)); gap: 12px; }
.chart { margin: 0; background: var(--panel); border-radius: 8px; padding: 14px 16px; display: grid; gap: 8px; min-width: 0; }
.chart figcaption { display: grid; margin-bottom: 2px; }
.chart figcaption span { color: var(--muted); font-size: 12.5px; }
.row { display: grid; grid-template-columns: 9.5em 1fr 4.6em; align-items: center; gap: 10px; font-size: 13px; border-radius: 4px; outline-offset: 2px; }
.row:hover .bar, .row:focus .bar { filter: brightness(1.12); }
.who { color: var(--fg2); }
.track { height: 16px; display: block; border-left: 1px solid var(--line); }
.bar { display: block; height: 100%; border-radius: 0 4px 4px 0; }
.val { font-variant-numeric: tabular-nums; font-weight: 600; text-align: right; }
.muted { color: var(--muted); font-weight: 400; }
.tablewrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; min-width: 560px; table-layout: fixed; font-size: 14px; font-variant-numeric: tabular-nums; }
thead th:first-child { width: 31%; }
th, td { text-align: left; padding: 8px 12px 8px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
thead th { font-weight: 600; color: var(--fg2); font-size: 13px; }
tbody th { font-weight: 600; text-transform: capitalize; }
td { font-weight: 600; }
small { display: block; font-weight: 400; color: var(--muted); font-size: 12.5px; text-transform: none; }
tr.total th, tr.total td { border-bottom: 0; }
.tablenote, footer { color: var(--muted); font-size: 12.5px; }
.extras { margin: 0; padding-left: 18px; color: var(--fg2); font-size: 14px; display: grid; gap: 4px; }
svg { display: block; width: 100%; height: auto; overflow: visible; }
.grid { stroke: var(--line); stroke-width: 1; }
.tick { fill: var(--muted); font-size: 11.5px; font-variant-numeric: tabular-nums; }
.line { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.l-none { stroke: var(--s-none); } .l-memory { stroke: var(--s-memory); } .l-dreaming { stroke: var(--s-dreaming); }
.dot { stroke: var(--panel); stroke-width: 2; }
.f-none { fill: var(--s-none); } .f-memory { fill: var(--s-memory); } .f-dreaming { fill: var(--s-dreaming); }
.hit { fill: transparent; outline-offset: 0; cursor: default; }
table.rounds { min-width: 760px; }
table.rounds thead th:first-child { width: 17%; }
.part { font-style: normal; font-weight: 400; color: var(--warn); }
.divider { font-size: 22px; }
.part2 { border-top: 1px solid var(--line); padding-top: 28px; }
#tip { position: fixed; z-index: 5; pointer-events: none; background: var(--fg); color: var(--bg); padding: 6px 9px; border-radius: 6px; font-size: 12.5px; max-width: 280px; }
@media (max-width: 480px) { .row { grid-template-columns: 7.2em 1fr 4.2em; gap: 6px; } }
</style>
</head>
<body>
<main>
<header>
  <h1>dream-lab results</h1>
  <p class="lede">The same coding tasks, done by Pi under three memory setups. For each setup: how often it got the task right, how long it took and how much credit it used.</p>
</header>
${roundSuites.map((s) => roundsSection(s.key, s.runs, s.extra, s.label ?? (modelDirs.length ? model : null))).join("\n")}
${roundSuites.length && suites.length ? `<header class="part2"><h2 class="divider">First experiment: memory learned once, then fixed</h2><p class="lede">Here memory came only from the learning tasks and didn't change during the eval tasks. Each task was run several times from that same memory.</p></header>` : ""}
${suites.map((s) => suiteSection(s.key, s.runs, s.label)).join("\n")}
<footer>
  Built ${today} from .dream-state/evals${model ? `, model ${esc(model)}` : ""}. Cost is tokens at API list prices, an estimate: on a Claude login the runs come out of usage limits, not a bill. Time is how long Pi took on each task.
</footer>
</main>
<div id="tip" hidden></div>
<script>
const tip = document.getElementById("tip");
const show = (el, x, y) => { tip.textContent = el.dataset.tip; tip.hidden = false;
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = Math.max(8, Math.min(x + 12, innerWidth - w - 8)) + "px";
  tip.style.top = (y + h + 24 > innerHeight ? y - h - 10 : y + 16) + "px"; };
for (const row of document.querySelectorAll("[data-tip]")) {
  row.addEventListener("mousemove", (e) => show(row, e.clientX, e.clientY));
  row.addEventListener("mouseleave", () => { tip.hidden = true; });
  row.addEventListener("focus", () => { const r = row.getBoundingClientRect(); show(row, r.left + Math.min(120, r.width / 2), r.top); });
  row.addEventListener("blur", () => { tip.hidden = true; });
}
</script>
</body>
</html>
`;
fs.writeFileSync(OUT, html);
const tag = (s) => (s.label ? ` (${s.label})` : "");
console.log(`Wrote ${OUT} (${[...roundSuites.map((s) => `${s.key} rounds${tag(s)}: ${s.runs.length} runs`), ...suites.map((s) => `${s.key}${tag(s)}: ${s.runs.length} runs`)].join(", ")})`);
