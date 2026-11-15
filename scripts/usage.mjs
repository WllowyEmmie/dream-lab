#!/usr/bin/env node
// Adds up tokens and cost from Pi session files and appends one CSV row per
// session (AI-21). Prints a one-line total for reports, e.g. "12.3k tokens / $0.0412".
//
//   node scripts/usage.mjs --kind task --out .dream-state/usage.csv a.jsonl b.jsonl
//
// Pi writes a "usage" block on every assistant reply, and "usage" entries for
// other model calls (cache warming, compaction summaries). Both count here.
// Cost: Pi's own figure when it has one. The claude-bridge provider reports $0,
// so then the cost is worked out from Pi's price list (models-store.json,
// dollars per million tokens) and the row is marked "list-price". Either way
// it's an API-price estimate on a Claude login, not your bill.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const agentDir = process.env.PI_CODING_AGENT_DIR || path.join(os.homedir(), ".pi", "agent");
const prices = {};   // model id -> { input, output, cacheRead, cacheWrite } per million tokens
try {
  const store = JSON.parse(fs.readFileSync(path.join(agentDir, "models-store.json"), "utf8"));
  for (const provider of Object.values(store))
    for (const m of provider?.models ?? [])
      if (m?.id && m.cost && !prices[m.id]) prices[m.id] = m.cost;
} catch { /* no price list: rows without a cost are marked "unknown" */ }
const listPrice = (model, u) => {
  const p = prices[model];
  if (!p) return null;
  return ((u.input ?? 0) * (p.input ?? 0) + (u.output ?? 0) * (p.output ?? 0) +
          (u.cacheRead ?? 0) * (p.cacheRead ?? 0) + (u.cacheWrite ?? 0) * (p.cacheWrite ?? 0)) / 1e6;
};

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(name);
  if (i === -1) return def;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const kind = opt("--kind", "task");
const out = opt("--out", ".dream-state/usage.csv");
const date = opt("--date", new Date().toISOString().slice(0, 10));
const jsonIdx = args.indexOf("--json");      // print totals as JSON, not text
const asJson = jsonIdx !== -1;
if (asJson) args.splice(jsonIdx, 1);
// Arguments are session files, or folders searched for *.jsonl (subagent
// sessions live in subfolders).
const walk = (p) => {
  let st;
  try { st = fs.statSync(p); } catch { return []; }
  if (!st.isDirectory()) return [p];
  return fs.readdirSync(p).flatMap((n) => walk(path.join(p, n))).filter((f) => f.endsWith(".jsonl"));
};
const files = args.flatMap(walk);
const sum = { sessions: 0, turns: 0, input: 0, output: 0, cacheRead: 0, cacheWrite: 0, tokens: 0, cost: 0 };

const header = "date,kind,session,model,turns,input,output,cache_read,cache_write,total_tokens,cost_usd,cost_source\n";
const csv = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));

let allTokens = 0, allCost = 0;
const rows = [];
for (const file of files) {
  let text;
  try { text = fs.readFileSync(file, "utf8"); } catch { continue; }
  const t = { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0, cost: 0, turns: 0 };
  const sources = new Set();
  const models = new Set();
  let id = path.basename(file, ".jsonl");
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    let e;
    try { e = JSON.parse(line); } catch { continue; }
    if (e.type === "session" && e.id) id = e.id;
    const u = e.message?.usage ?? e.usage;
    if (!u || typeof u !== "object") continue;
    if (e.message?.role === "assistant") t.turns++;
    const m = e.message?.model ?? e.model;
    if (m) models.add(m);
    t.input += u.input ?? 0;
    t.output += u.output ?? 0;
    t.cacheRead += u.cacheRead ?? 0;
    t.cacheWrite += u.cacheWrite ?? 0;
    t.total += u.totalTokens ?? 0;
    const own = u.cost?.total ?? 0;
    if (own > 0 || !u.totalTokens) { t.cost += own; sources.add("provider"); }
    else {
      const est = listPrice(m, u);
      if (est === null) sources.add("unknown");
      else { t.cost += est; sources.add("list-price"); }
    }
  }
  allTokens += t.total;
  allCost += t.cost;
  sum.sessions++; sum.turns += t.turns; sum.input += t.input; sum.output += t.output;
  sum.cacheRead += t.cacheRead; sum.cacheWrite += t.cacheWrite; sum.tokens += t.total; sum.cost += t.cost;
  rows.push([date, kind, id, [...models].join(" "), t.turns, t.input, t.output,
             t.cacheRead, t.cacheWrite, t.total, t.cost.toFixed(6), [...sources].join(" ")].map(csv).join(","));
}

if (rows.length && out !== "none") {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  if (!fs.existsSync(out)) fs.writeFileSync(out, header);
  fs.appendFileSync(out, rows.join("\n") + "\n");
}
const k = allTokens >= 1000 ? `${(allTokens / 1000).toFixed(1)}k` : `${allTokens}`;
if (asJson) console.log(JSON.stringify({ ...sum, cost: Number(sum.cost.toFixed(6)) }));
else console.log(`${k} tokens / $${allCost.toFixed(4)}`);
