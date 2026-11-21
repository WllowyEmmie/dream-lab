#!/usr/bin/env node
// Helper for scripts/run-evals.sh (AI-23): lists tasks, records one run per line
// in a runs file, and builds results.json from it.
//
//   node scripts/eval-results.mjs tasks [group] [tasks.json]
//   node scripts/eval-results.mjs has <runs> <setup> <task> <repeat>
//   node scripts/eval-results.mjs record <runs>          (fields come from RUN_* env vars)
//   node scripts/eval-results.mjs summarize <runs> <results.json> [state dir]
import fs from "node:fs";
import path from "node:path";

const [cmd, ...a] = process.argv.slice(2);
const readRuns = (file) => {
  if (!fs.existsSync(file)) return [];
  const rows = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const last = new Map();                       // a rerun replaces the earlier row
  for (const r of rows) last.set(`${r.setup}|${r.task}|${r.repeat}`, r);
  return [...last.values()];
};
const walk = (p) => {
  let st;
  try { st = fs.statSync(p); } catch { return []; }
  if (!st.isDirectory()) return [p];
  return fs.readdirSync(p).flatMap((n) => walk(path.join(p, n))).filter((f) => f.endsWith(".jsonl"));
};

if (cmd === "tasks") {
  const { tasks } = JSON.parse(fs.readFileSync(a[1] || "tasks/tasks.json", "utf8"));
  for (const t of tasks) if (!a[0] || a[0] === "all" || t.group === a[0]) console.log(`${t.id} ${t.group}`);

} else if (cmd === "has") {
  const [file, setup, task, repeat] = a;
  const hit = readRuns(file).some((r) => r.setup === setup && r.task === task && String(r.repeat) === repeat);
  process.exit(hit ? 0 : 1);

} else if (cmd === "record") {
  const e = process.env;
  // Which memory files did the agent open? Looks at tool calls in the session
  // files; an append (">> memory/inbox.md") doesn't count as reading. Approximate.
  const memory = new Set();
  for (const f of walk(e.RUN_SESSIONS || "")) {
    for (const line of fs.readFileSync(f, "utf8").split("\n")) {
      if (!line.includes("toolCall")) continue;
      let entry;
      try { entry = JSON.parse(line); } catch { continue; }
      for (const b of entry.message?.content ?? []) {
        if (b?.type !== "toolCall") continue;
        const text = JSON.stringify(b.arguments ?? {});
        for (const m of text.matchAll(/(>>\s*)?memory[\\/]+([\w-]+\.md)/g)) if (!m[1]) memory.add(m[2]);
      }
    }
  }
  const usage = JSON.parse(e.RUN_USAGE || "{}");
  const row = {
    date: new Date().toISOString(), setup: e.RUN_SETUP, group: e.RUN_GROUP, task: e.RUN_TASK,
    repeat: Number(e.RUN_REPEAT), passed: e.RUN_PASSED === "yes",
    visible_passed: e.RUN_VISIBLE ? e.RUN_VISIBLE === "yes" : e.RUN_PASSED === "yes",
    hidden_passed: Number(e.RUN_HIDDEN_PASSED || 0), hidden_total: Number(e.RUN_HIDDEN_TOTAL || 0),
    test_edited: e.RUN_TEST_EDITED === "yes",
    timed_out: e.RUN_TIMED_OUT === "yes", seconds: Number(e.RUN_SECONDS || 0),
    turns: usage.turns ?? 0, tokens: usage.tokens ?? 0, cost_usd: usage.cost ?? 0,
    memory_files_read: [...memory].sort(),
  };
  fs.mkdirSync(path.dirname(a[0]), { recursive: true });
  fs.appendFileSync(a[0], JSON.stringify(row) + "\n");
  const hidden = row.hidden_total ? `  visible ${row.visible_passed ? "ok" : "failed"}, hidden ${row.hidden_passed}/${row.hidden_total},` : "";
  console.log(`${row.passed ? "PASS" : "FAIL"}${hidden}  ${row.turns} turns, ${(row.tokens / 1000).toFixed(1)}k tokens, $${row.cost_usd.toFixed(4)}`);

} else if (cmd === "line") {
  // One Slack message: a round of one setup, or (setup "all") the whole rounds run.
  const [file, setup, round, extraFile, suite, rounds] = a;
  const runs = readRuns(file);
  const extra = (() => { try { return fs.readFileSync(extraFile, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l)); } catch { return []; } })();
  const name = { none: "No memory", memory: "Memory", dreaming: "Memory + dreaming" };
  const tok = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(2)}M` : `${(n / 1000).toFixed(1)}k`);
  const time = (s) => (s >= 3600 ? `${Math.floor(s / 3600)}h ${Math.round((s % 3600) / 60)}m` : `${Math.round(s / 60)}m`);
  const sumUp = (rs) => ({ n: rs.length, ok: rs.filter((r) => r.passed).length, s: rs.reduce((x, r) => x + r.seconds, 0),
    t: rs.reduce((x, r) => x + r.tokens, 0), c: rs.reduce((x, r) => x + r.cost_usd, 0) });
  const similar = (rs) => { const s = rs.filter((r) => r.group === "similar"); return s.length ? `, similar ${s.filter((r) => r.passed).length}/${s.length}` : ""; };
  if (setup !== "all") {
    const rs = runs.filter((r) => r.setup === setup && String(r.repeat) === round);
    const s = sumUp(rs);
    const mem = extra.find((e) => e.kind === "memory" && e.setup === setup && String(e.round) === round);
    const dream = extra.find((e) => e.kind === "dream" && e.setup === setup && String(e.round) === round);
    const lines = [`:bar_chart: dream-lab eval, ${suite} tasks: *${name[setup] ?? setup}*, round ${round} of ${rounds} done`,
      `Passed ${s.ok}/${s.n}${similar(rs)} · ${time(s.s)} · ${tok(s.t)} tokens · $${s.c.toFixed(2)}`];
    if (mem) lines.push(`Memory: ${mem.memory_tokens} tokens`);
    if (dream) lines.push(`Dreaming pass after it: ${tok(dream.tokens)} tokens, $${dream.cost_usd.toFixed(2)}, judge ${dream.judge_score ?? "–"}/5, memory ${dream.memory_before} to ${dream.memory_after} tokens`);
    console.log(lines.join("\n"));
  } else {
    const lines = [`:white_check_mark: dream-lab eval finished: ${suite} tasks, ${rounds} rounds`];
    for (const id of ["none", "memory", "dreaming"]) {
      const rs = runs.filter((r) => r.setup === id);
      if (!rs.length) continue;
      const s = sumUp(rs);
      lines.push(`*${name[id]}*: passed ${s.ok}/${s.n}${similar(rs)} · ${time(s.s)} · ${tok(s.t)} tokens · $${s.c.toFixed(2)}`);
    }
    lines.push("Build the results page: node scripts/build-report.mjs");
    console.log(lines.join("\n"));
  }

} else if (cmd === "summarize") {
  const [file, out, state] = a;
  const runs = readRuns(file);
  const avg = (xs) => (xs.length ? xs.reduce((s, x) => s + x, 0) / xs.length : 0);
  // hidden_score: average share of hidden tests passed (partial credit), where a task has them.
  const hiddenScore = (rs) => {
    const h = rs.filter((r) => r.hidden_total > 0);
    return h.length ? Number(avg(h.map((r) => r.hidden_passed / r.hidden_total)).toFixed(3)) : null;
  };
  const stats = (rs) => ({
    runs: rs.length, passed: rs.filter((r) => r.passed).length,
    visible_passed: rs.filter((r) => r.visible_passed ?? r.passed).length, hidden_score: hiddenScore(rs),
    pass_rate: rs.length ? Number((rs.filter((r) => r.passed).length / rs.length).toFixed(3)) : null,
    avg_turns: Number(avg(rs.map((r) => r.turns)).toFixed(1)),
    avg_tokens: Math.round(avg(rs.map((r) => r.tokens))),
    avg_cost_usd: Number(avg(rs.map((r) => r.cost_usd)).toFixed(4)),
    avg_memory_files_read: Number(avg(rs.map((r) => r.memory_files_read.length)).toFixed(2)),
  });
  const setups = {};
  for (const setup of ["none", "memory", "dreaming"]) {
    const rs = runs.filter((r) => r.setup === setup);
    if (!rs.length) continue;
    setups[setup] = { all: stats(rs) };
    for (const g of ["similar", "new", "different"]) setups[setup][g] = stats(rs.filter((r) => r.group === g));
  }
  const tasks = {};
  for (const r of runs.filter((r) => r.setup !== "learning")) {
    tasks[r.task] ??= { group: r.group };
    const t = (tasks[r.task][r.setup] ??= { runs: 0, passed: 0 });
    t.runs++; if (r.passed) t.passed++;
  }
  const result = { generated: new Date().toISOString(), setups, tasks };
  const learning = runs.filter((r) => r.setup === "learning");
  if (learning.length) result.learning = stats(learning);
  // What the dreaming pass did, if run-evals.sh saved it.
  try { result.dreaming_pass = JSON.parse(fs.readFileSync(path.join(state, "dream.json"), "utf8")); } catch {}
  fs.writeFileSync(out, JSON.stringify(result, null, 2) + "\n");
  for (const [name, s] of Object.entries(setups)) {
    const cell = (g) => (s[g].runs ? `${s[g].passed}/${s[g].runs}` : "-");
    console.log(`${name.padEnd(9)} similar ${cell("similar").padEnd(6)} new ${cell("new").padEnd(6)} different ${cell("different").padEnd(6)} all ${cell("all")}`);
  }

} else {
  console.error("usage: eval-results.mjs tasks|has|record|summarize ...");
  process.exit(2);
}
