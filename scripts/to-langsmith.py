#!/usr/bin/env python3
"""Upload eval runs to LangSmith as traces, so you can see what the agent did.

Each run becomes one trace: the task prompt at the top, then every model turn
and tool call (bash, read, edit, subagent...) in order, with the code-reviewer
and fixer subagents nested under the call that started them. The trace is
tagged with its setup and carries feedback scores: passed, hidden tests passed,
and whether the agent read memory/.

  python scripts/to-langsmith.py --suite hard --model claude-haiku-5-5 --label harness-v2 --task 05-quote-vat --round 1
  python scripts/to-langsmith.py ... --dry-run          # write the traces to langsmith-dry-run.json instead

Needs: pip install langsmith, and LANGSMITH_API_KEY in .env (never commit it).
Sessions are read from the eval work folder (../dream-lab-evals/...).
"""
import argparse, glob, json, os, sys, uuid
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETUPS = ["none", "memory", "dreaming"]
MAX_TEXT = 6000


def load_env():
    path = os.path.join(REPO, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_prices():
    """Pi's price list (dollars per million tokens), as scripts/usage.mjs reads it."""
    d = os.environ.get("PI_CODING_AGENT_DIR") or os.path.join(os.path.expanduser("~"), ".pi", "agent")
    prices = {}
    try:
        store = json.load(open(os.path.join(d, "models-store.json"), encoding="utf-8"))
        for prov in store.values():
            for m in (prov or {}).get("models", []) if isinstance(prov, dict) else []:
                if m.get("id") and m.get("cost") and m["id"] not in prices:
                    prices[m["id"]] = m["cost"]
    except Exception:
        pass
    return prices


PRICES = load_prices()


def ts(v):
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
    return datetime.fromisoformat(str(v).replace("Z", "+00:00"))


def text_of(content):
    if isinstance(content, str):
        return content[:MAX_TEXT]
    out = []
    for b in content or []:
        if b.get("type") == "text":
            out.append(b.get("text", ""))
        elif b.get("type") == "thinking":
            out.append("[thinking] " + b.get("thinking", ""))
    return "\n".join(out)[:MAX_TEXT]


def long_path(path):
    """Windows refuses to open paths over 260 characters unless they start with \\?\\."""
    path = os.path.abspath(path)
    if os.name == "nt" and not path.startswith("\\\\?\\"):
        path = "\\\\?\\" + path
    return path


def read_session(path):
    return [json.loads(l) for l in open(long_path(path), encoding="utf-8") if l.strip()]


def build(path, name, kids=None):
    """Turn one Pi session file into a nested dict of runs."""
    events = read_session(path)
    kids = list(kids or [])
    root = {"name": name, "run_type": "chain", "inputs": {}, "outputs": {}, "children": [],
            "start": ts(events[0]["timestamp"]), "end": ts(events[-1]["timestamp"])}
    calls = {}
    last = root["start"]
    tokens = 0
    for e in events:
        if e.get("type") != "message":
            continue
        m = e["message"]
        # Pi stamps an assistant message with when the model started (message
        # timestamp) and when it finished (event timestamp); a tool result with when
        # the tool finished, plus how long it ran (durationMs).
        t = ts(e["timestamp"])
        role = m.get("role")
        if role == "user" and not root["inputs"]:
            root["inputs"] = {"prompt": text_of(m["content"])}
        elif role == "assistant":
            u = m.get("usage") or {}
            tokens += u.get("totalTokens", 0)
            model = m.get("model", "model")
            usage = {"input_tokens": u.get("input", 0) + u.get("cacheRead", 0) + u.get("cacheWrite", 0),
                     "output_tokens": u.get("output", 0)}
            usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
            p = PRICES.get(model)
            if p:  # list-price estimate, like scripts/usage.mjs (Pi records $0 on a Claude login)
                usage["input_cost"] = (u.get("input", 0) * p.get("input", 0) + u.get("cacheRead", 0) * p.get("cacheRead", 0)
                                       + u.get("cacheWrite", 0) * p.get("cacheWrite", 0)) / 1e6
                usage["output_cost"] = u.get("output", 0) * p.get("output", 0) / 1e6
                usage["total_cost"] = usage["input_cost"] + usage["output_cost"]
            llm = {"name": model, "run_type": "llm", "start": ts(m.get("timestamp", e["timestamp"])), "end": t,
                   "inputs": {}, "outputs": {"text": text_of(m["content"])}, "usage": usage, "model": model,
                   "children": []}
            root["children"].append(llm)
            for b in m["content"]:
                if b.get("type") == "toolCall":
                    tool = {"name": b["name"], "run_type": "tool", "start": t, "end": t,
                            "inputs": b.get("arguments") or {}, "outputs": {}, "children": []}
                    if b["name"] == "subagent" and kids:
                        tool["children"].append(kids.pop(0))
                    calls[b["id"]] = tool
                    root["children"].append(tool)
            if m["content"] and not any(b.get("type") == "toolCall" for b in m["content"]):
                root["outputs"] = {"final": text_of(m["content"])}
        elif role == "toolResult":
            tool = calls.get(m.get("toolCallId"))
            if tool:
                tool["outputs"] = {"result": text_of(m["content"])}
                tool["end"] = ts(m.get("timestamp", e["timestamp"]))
                if m.get("durationMs") is not None:
                    tool["start"] = max(tool["start"], tool["end"] - timedelta(milliseconds=m["durationMs"]))
                tool["error"] = "error" if m.get("isError") else None
        last = t
    root["end"] = max(root["end"], last)
    root["tokens"] = tokens
    return root


def run_traces(args):
    tag = (args.model or "default") + (f"-{args.label}" if args.label else "")
    base = os.environ.get("EVAL_WORK") or os.path.join(os.path.dirname(REPO), "dream-lab-evals")
    if args.model or args.label:
        base = os.path.join(base, "models", tag)
    work = os.path.join(base, "rounds", args.suite) if args.suite != "easy" else os.path.join(base, "rounds", "easy")
    results = os.path.join(REPO, ".dream-state", "evals", *(["models", tag] if (args.model or args.label) else []),
                           f"rounds-{args.suite}.jsonl")
    rows = {}
    for l in open(results, encoding="utf-8"):
        r = json.loads(l)
        rows[(r["setup"], r["task"], r["repeat"])] = r
    traces = []
    for setup in args.setups:
        for (s, task, rnd), row in sorted(rows.items()):
            if s != setup or (args.task and task != args.task) or (args.round and rnd != args.round):
                continue
            d = os.path.join(work, "sessions", setup, f"round-{rnd}", f"{task}-r{rnd}")
            mains = sorted(glob.glob(os.path.join(d, "*.jsonl")))
            if not mains:
                print(f"no session for {setup} {task} round {rnd} in {d}", file=sys.stderr)
                continue
            kid_files = sorted(glob.glob(os.path.join(d, "*", "tasks", "*.jsonl")))
            kids = [build(f, "subagent session") for f in kid_files]
            tr = build(mains[0], f"{setup} · {task} · round {rnd}", kids)
            read_memory = any(c["run_type"] == "tool" and "memory/" in json.dumps(c["inputs"]) for c in tr["children"])
            tr["outputs"].update({"passed": row["passed"], "visible_passed": row.get("visible_passed"),
                                  "hidden": f'{row.get("hidden_passed")}/{row.get("hidden_total")}'})
            tr["tags"] = [setup, args.suite, tag, row.get("group", "")]
            tr["metadata"] = {"setup": setup, "task": task, "round": rnd, "group": row.get("group"),
                              "model": tag, "suite": args.suite, "tokens": row.get("tokens"), "cost_usd": row.get("cost_usd")}
            tr["feedback"] = {"passed": 1 if row["passed"] else 0,
                              "hidden_passed": (row["hidden_passed"] / row["hidden_total"]) if row.get("hidden_total") else None,
                              "read_memory": 1 if read_memory else 0}
            traces.append(tr)
    return traces


def to_json(r):
    return {k: (v.isoformat() if isinstance(v, datetime) else [to_json(c) for c in v] if k == "children" else v)
            for k, v in r.items()}


def upload(traces, project):
    from langsmith import Client
    from langsmith.run_trees import RunTree
    client = Client()

    def make(node, parent):
        extra = {"metadata": dict(node.get("metadata", {}))}
        if node.get("model"):
            extra["metadata"].update(ls_provider="anthropic", ls_model_name=node["model"])
        kw = dict(name=node["name"], run_type=node["run_type"], inputs=node["inputs"],
                  start_time=node["start"], extra=extra, tags=node.get("tags"))
        rt = parent.create_child(**kw) if parent else RunTree(project_name=project, **kw)
        if node.get("usage"):
            rt.set(usage_metadata=node["usage"])
        rt.end(outputs=dict(node["outputs"]), end_time=node["end"], error=node.get("error"))
        rt.post()
        for c in node["children"]:
            make(c, rt)
        return rt

    def shift(node, by):
        node["start"] += by
        node["end"] += by
        for c in node["children"]:
            shift(c, by)

    # LangSmith only accepts runs that started within the last 24 hours. So the traces
    # are replayed back to back, in the order they really ran, ending a minute ago:
    # each keeps its own steps and timings, only the waits between runs are dropped.
    # The real start time is kept in the metadata as ran_at.
    traces = sorted(traces, key=lambda t: t["start"])
    gap = timedelta(seconds=1)
    total = sum((t["end"] - t["start"] for t in traces), timedelta()) + gap * len(traces)
    if total > timedelta(hours=23):
        sys.exit(f"These runs add up to {total}, more than LangSmith's 24-hour window. Upload fewer at once (e.g. one --setup).")
    cursor = datetime.now(timezone.utc) - timedelta(minutes=1) - total
    for tr in traces:
        tr["metadata"]["ran_at"] = tr["start"].isoformat()
        shift(tr, cursor - tr["start"])
        cursor = tr["end"] + gap
    for i, tr in enumerate(traces, 1):
        root = make(tr, None)
        for key, score in tr["feedback"].items():
            if score is not None:
                client.create_feedback(root.id, key=key, score=score)
        if hasattr(client, "flush"):
            client.flush()
        print(f"[{i}/{len(traces)}] sent {tr['name']}  passed={tr['feedback']['passed']}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--suite", default="hard", choices=["easy", "hard", "veryhard"])
    p.add_argument("--model"); p.add_argument("--label")
    p.add_argument("--task"); p.add_argument("--round", type=int)
    p.add_argument("--setup", action="append", dest="setups", choices=SETUPS)
    p.add_argument("--project", help="LangSmith project name (default dream-lab-<model>-<suite>)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    a.setups = a.setups or SETUPS
    traces = run_traces(a)
    if not traces:
        sys.exit("No runs matched.")
    if a.dry_run:
        out = os.path.join(REPO, ".dream-state", "langsmith-dry-run.json")
        json.dump([to_json(t) for t in traces], open(out, "w", encoding="utf-8"), indent=1, default=str)
        for t in traces:
            print(f"{t['name']}: {len(t['children'])} steps, read_memory={t['feedback']['read_memory']}, passed={t['feedback']['passed']}")
        print(f"Wrote {out}")
        return
    load_env()
    if not os.environ.get("LANGSMITH_API_KEY"):
        sys.exit("Set LANGSMITH_API_KEY in .env first.")
    os.environ.setdefault("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    project = a.project or f"dream-lab-{(a.model or 'default')}{'-' + a.label if a.label else ''}-{a.suite}"
    models = {"claude-haiku-5-5"} if "haiku" in (a.model or "") else set()
    missing = [mm for mm in models if mm not in PRICES]
    if not PRICES or missing:
        print("No price found in Pi's models-store.json for this model, so cost will show as $0.", file=sys.stderr)
    upload(traces, project)
    print(f"Done. Open https://smith.langchain.com and look for the project {project}.")


if __name__ == "__main__":
    main()
