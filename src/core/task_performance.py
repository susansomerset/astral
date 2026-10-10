"""Task Performance roster — admin-grade script (NOT under the test bible).

Rolls dispatch_ledger runs + agent_timesheets calls up the tree
Total > Task Group > Task Key > Version (agent_task row) > Candidate > Ledger line.

Version link: dispatch_ledger has no task_key_uuid, so a batch's version comes from its
timesheet rows (batch_id -> task_key_uuid). A batch's spend/tokens always cover ALL of its
timesheet rows (every hop); only the *version bucket* is chosen from the primary-hop uuid.
Spend is read straight from timesheets (platform_cost else stored calc_cost_*); never re-priced.
"""
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.candidate import build_candidate_token_view, get_candidate, rubric_dispatch_error
from src.data.database import _agent_task_prompt_texts, _get_connection, get_agent
from src.utils.config import TASK_CONFIG, empty_render_for_prompts

NO_AGENT_TASK = "(no agent_task)"
NO_CALL = "(no LLM call)"
UNKNOWN_VERSION = "(unknown version)"

# Additive per-batch fields (summed up the tree).
SUM_KEYS = (
    "batches", "completed", "fail_calls", "ok_calls", "subjects", "passed", "failed", "errors", "retries",
    "in_tokens", "nocache_tokens", "cache_write_tokens", "cache_read_tokens", "out_tokens",
    "duration", "dur_subjects",
    "spend", "spend_input", "spend_cache_write", "spend_cache_read", "spend_output", "spend_platform_only",
)


def _norm_ts(value: Optional[str], end_of_day: bool) -> Optional[str]:
    """ISO / date / datetime-local string -> 'YYYY-MM-DD HH:MM:SS' (DB stores UTC, space-separated)."""
    v = (value or "").strip().replace("T", " ")
    if not v:
        return None
    if len(v) == 10:  # bare date
        return v + (" 23:59:59" if end_of_day else " 00:00:00")
    return v[:19]


def _digits14(ts: Optional[str]) -> str:
    return re.sub(r"\D", "", ts or "")[:14].ljust(14, "0")


def _seconds(start: Optional[str], end: Optional[str]) -> Optional[float]:
    """Wall-clock seconds between two ledger timestamps (UTC, 'YYYY-MM-DD HH:MM:SS'); None if either is missing/bad."""
    try:
        return (datetime.strptime(end[:19], "%Y-%m-%d %H:%M:%S") - datetime.strptime(start[:19], "%Y-%m-%d %H:%M:%S")).total_seconds()
    except (TypeError, ValueError):
        return None


def _is_fail(perf: Optional[str]) -> bool:
    # Legacy rows carry NULL / ok / pass / completed / normal ... — only an explicit 'failure' is a failed call.
    return (perf or "").strip().lower() == "failure"


class _Agg:
    """Accumulates per-batch dicts into one tree node's metrics."""

    def __init__(self) -> None:
        self.m = dict.fromkeys(SUM_KEYS, 0)
        self.spend_runs: List[float] = []  # per-run stats only count batches that made >=1 LLM call
        self.out_runs: List[int] = []
        self.dur_runs: List[float] = []  # COMPLETED/FAILED runs only; INTERRUPTED end times are restart stamps, not run lengths
        self.types: set = set()
        self.last_ok: Optional[str] = None
        self.last_clean: Optional[str] = None

    def add(self, ln: Dict[str, Any]) -> "_Agg":
        for k in SUM_KEYS:
            self.m[k] += ln[k]
        if ln["calls"]:
            self.spend_runs.append(ln["spend"])
            self.out_runs.append(ln["out_tokens"])
        if ln["dur"] is not None:
            self.dur_runs.append(ln["dur"])
        if ln["entity_type"]:
            self.types.add(ln["entity_type"])
        # Successful run = COMPLETED with >=1 pass; clean run = COMPLETED, >=1 processed, 0 errors.
        if ln["completed"] and ln["passed"] > 0 and (self.last_ok or "") < ln["started_at"]:
            self.last_ok = ln["started_at"]
        if ln["completed"] and ln["subjects"] > 0 and ln["errors"] == 0 and (self.last_clean or "") < ln["started_at"]:
            self.last_clean = ln["started_at"]
        return self

    def row(self) -> Dict[str, Any]:
        m = self.m
        n = len(self.spend_runs)
        avg = (sum(self.spend_runs) / n) if n else None
        sd = math.sqrt(sum((x - avg) ** 2 for x in self.spend_runs) / n) if n else None
        out = {k: (round(v, 8) if isinstance(v, float) else v) for k, v in m.items()}
        d = self.dur_runs
        dn = len(d)
        dav = (sum(d) / dn) if dn else None
        out.update({
            "dur_run_avg": round(dav, 2) if dn else None,
            "dur_run_min": round(min(d), 2) if dn else None,
            "dur_run_max": round(max(d), 2) if dn else None,
            "dur_run_sd": round(math.sqrt(sum((x - dav) ** 2 for x in d) / dn), 2) if dn else None,
            "dur_entity": round(m["duration"] / m["dur_subjects"], 3) if m["dur_subjects"] else None,
            "entity_type": ", ".join(sorted(self.types)),
            "unresolved": m["subjects"] - m["passed"] - m["failed"] - m["errors"],
            "tokens": m["in_tokens"] + m["out_tokens"],
            "cache_hit_pct": round(100.0 * m["cache_read_tokens"] / m["in_tokens"], 2) if m["in_tokens"] else None,
            "out_avg": round(sum(self.out_runs) / n, 2) if n else None,
            "out_min": min(self.out_runs) if n else None,
            "out_max": max(self.out_runs) if n else None,
            "spend_run_avg": round(avg, 8) if n else None,
            "spend_run_min": round(min(self.spend_runs), 8) if n else None,
            "spend_run_max": round(max(self.spend_runs), 8) if n else None,
            "spend_run_sd": round(sd, 8) if n else None,
            "spend_entity": round(m["spend"] / m["subjects"], 8) if m["subjects"] else None,
            "last_success": self.last_ok,
            "last_clean": self.last_clean,
        })
        return out


def _line(led: Dict[str, Any], ts_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """One ledger batch -> additive metrics from its ledger counts + all its timesheet rows."""
    ln = dict.fromkeys(SUM_KEYS, 0)
    ln.update(
        batches=1, completed=1 if led["status"] == "COMPLETED" else 0,
        subjects=led["total_processed"] or 0, passed=led["total_passed"] or 0,
        failed=led["total_failed"] or 0, errors=led["total_errors"] or 0,
        calls=len(ts_rows), entity_type=led["entity_type"], started_at=led["started_at"] or "",
    )
    dur = _seconds(led["started_at"], led["completed_at"]) if led["status"] in ("COMPLETED", "FAILED") else None
    ln["dur"] = dur
    if dur is not None:
        ln["duration"], ln["dur_subjects"] = dur, ln["subjects"]
    last_ok: Dict[str, str] = {}   # per (hop uuid): latest successful call time
    fails: Dict[str, List[str]] = {}
    for r in ts_rows:
        u, t = r["task_key_uuid"] or "", r["created_at"] or ""
        if _is_fail(r["agent_performance"]):
            ln["fail_calls"] += 1
            fails.setdefault(u, []).append(t)
        else:
            ln["ok_calls"] += 1
            last_ok[u] = max(last_ok.get(u, ""), t)
        rd, wr, nc = r["cache_read_tokens"] or 0, r["cache_write_tokens"] or 0, r["total_no_cache_input_tokens"] or 0
        ln["cache_read_tokens"] += rd
        ln["cache_write_tokens"] += wr
        ln["nocache_tokens"] += nc
        ln["in_tokens"] += rd + wr + nc
        ln["out_tokens"] += r["total_output_tokens"] or 0
        comp = {k: r[f"calc_cost_{k}"] or 0.0 for k in ("no_cache_input", "cache_write", "cache_read", "output")}
        calc = sum(comp.values())
        ln["spend_input"] += comp["no_cache_input"]
        ln["spend_cache_write"] += comp["cache_write"]
        ln["spend_cache_read"] += comp["cache_read"]
        ln["spend_output"] += comp["output"]
        pc = r["platform_cost"]
        ln["spend"] += pc if pc is not None else calc
        ln["spend_platform_only"] += (pc - calc) if pc is not None else 0.0  # platform total with no per-component split
    # Retry = a failed call in a hop that later got a successful call (the bad response was tried again).
    ln["retries"] = sum(1 for u, fs in fails.items() if u in last_ok for t in fs if t < last_ok[u])
    return ln


def _resolve_version(
    led: Dict[str, Any], ts_rows: List[Dict[str, Any]], at: Dict[str, Dict[str, Any]]
) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """(agent task_key, version label, agent_task record or None) for a ledger batch.

    The ledger key is a *dispatch* key and can differ from the agent_task key (meteorite_grade_get runs
    agent task grade_get, via TASK_CONFIG master_task_key). Task key = master_task_key, else the ledger key
    if the batch used one of its versions, else the single agent task the batch's timesheets point at.
    """
    key = TASK_CONFIG.get(led["task_key"], {}).get("master_task_key") or led["task_key"]
    if not ts_rows:
        return key, NO_CALL, None
    uuids = {r["task_key_uuid"] for r in ts_rows if r["task_key_uuid"]}
    known = {u for u in uuids if u in at}
    if not any(at[u]["task_key"] == key for u in known):
        keys = {at[u]["task_key"] for u in known}
        if len(keys) == 1:  # dispatch key unmapped, but every known version belongs to one agent task
            key = next(iter(keys))
    mine = [u for u in known if at[u]["task_key"] == key]
    if mine:  # several versions of the same task in one batch -> most recently used
        u = max(mine, key=lambda x: max(r["created_at"] or "" for r in ts_rows if r["task_key_uuid"] == x))
        return key, _vlabel(u, at[u]), at[u]
    if len(uuids) == 1 and not known:  # single version whose agent_task row is gone
        return key, f"??-{next(iter(uuids))}", None
    return key, UNKNOWN_VERSION, None


def _vlabel(uuid: str, rec: Dict[str, Any]) -> str:
    return f"{_digits14(rec['updated_at'])}-{uuid}"


def _candidate_valid(rec: Dict[str, Any], cid: str, tk: str, cache: Dict[str, Any]) -> Tuple[Optional[bool], str]:
    """Would this version's prompts dispatch cleanly for this candidate? Same two gates a real dispatch uses:
    no empty-rendered {$TOKEN}s (candidate artifacts + rubric tokens) and no rubric error. None = not scoreable."""
    try:
        if cid not in cache["view"]:
            cand = get_candidate(cid)
            cache["view"][cid] = build_candidate_token_view(cand) if cand else None
        view = cache["view"][cid]
        if view is None:
            return None, "candidate not found"
        aid = (rec.get("agent_id") or "").strip()
        if aid not in cache["agent"]:
            cache["agent"][aid] = get_agent(aid) if aid else None
        texts = _agent_task_prompt_texts(rec, cache["agent"][aid])
        res = empty_render_for_prompts(texts, view, tk, entity_contexts={"rubric": {}})
        if (cid, tk) not in cache["rubric"]:
            cache["rubric"][(cid, tk)] = rubric_dispatch_error(cid, tk)
        err = cache["rubric"][(cid, tk)]
        notes = ([f"empty tokens: {', '.join(res['empty_tokens'])}"] if res["empty_render"] else []) + ([err] if err else [])
        return (not notes), "; ".join(notes)
    except Exception as exc:  # a scoring crash must not take the whole roster down
        return None, f"{type(exc).__name__}: {exc}"


def _ratio(pairs: List[Optional[bool]]) -> Optional[str]:
    scored = [p for p in pairs if p is not None]
    return f"{sum(scored)}/{len(scored)}" if scored else None


def build_task_performance(
    date_from: Optional[str] = None, date_to: Optional[str] = None,
    current_only: bool = False, candidate_id: Optional[str] = None,
    lines: Optional[Any] = None,  # None = no ledger lines; "all"; or (task_key, version, candidate) tuple
) -> Dict[str, Any]:
    conn = _get_connection()
    try:
        at = {
            r["task_key_uuid"]: dict(r) for r in conn.execute(
                "SELECT task_key_uuid, task_key, current, updated_at, task_group_name, task_group_order, task_seq,"
                " agent_id, user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d, nocache_prompt,"
                " system_prompt FROM agent_task"
            )
        }
        where, params = ["COALESCE(task_key,'') <> ''"], []
        f, t = _norm_ts(date_from, False), _norm_ts(date_to, True)
        if f:
            where.append("started_at >= ?"); params.append(f)
        if t:
            where.append("started_at <= ?"); params.append(t)
        if candidate_id:
            where.append("candidate_id = ?"); params.append(candidate_id)
        w = " AND ".join(where)
        ledger = [dict(r) for r in conn.execute(
            f"SELECT batch_id, task_key, candidate_id, entity_type, started_at, completed_at, status, total_processed,"
            f" total_passed, total_failed, total_errors FROM dispatch_ledger WHERE {w} ORDER BY started_at DESC", params)]
        ts_by_batch: Dict[str, List[Dict[str, Any]]] = {}
        for r in conn.execute(
            "SELECT batch_id, task_key_uuid, created_at, agent_performance, cache_write_tokens, cache_read_tokens,"
            " total_no_cache_input_tokens, total_output_tokens, calc_cost_cache_write, calc_cost_cache_read,"
            f" calc_cost_no_cache_input, calc_cost_output, platform_cost FROM agent_timesheets"
            f" WHERE batch_id IN (SELECT batch_id FROM dispatch_ledger WHERE {w})", params):
            ts_by_batch.setdefault(r["batch_id"], []).append(dict(r))
    finally:
        conn.close()

    # --- seed version nodes from agent_task (zero-run versions must show so they can be found with the Runs = None filter) ---
    ver: Dict[Tuple[str, str], Dict[str, Any]] = {}  # (task_key, label) -> {rec, agg, cands{cand: agg}, lines[]}
    for u, rec in at.items():
        if current_only and rec["current"] != 1:
            continue
        ver[(rec["task_key"], _vlabel(u, rec))] = {"rec": rec, "agg": _Agg(), "cands": {}, "lines": []}

    total, tasks = _Agg(), {}
    for led in ledger:
        rows = ts_by_batch.get(led["batch_id"], [])
        tk, label, rec = _resolve_version(led, rows, at)
        if current_only and not (rec and rec["current"] == 1):
            continue
        ln = _line(led, rows)
        v = ver.setdefault((tk, label), {"rec": rec, "agg": _Agg(), "cands": {}, "lines": []})
        cand = led["candidate_id"] or "(none)"
        v["agg"].add(ln)
        v["cands"].setdefault(cand, _Agg()).add(ln)
        v["lines"].append((cand, led, ln))
        tasks.setdefault(tk, _Agg()).add(ln)
        total.add(ln)

    # --- task -> group (from current version, else newest version, else none) ---
    by_task: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for (tk, label), v in ver.items():
        by_task.setdefault(tk, []).append((label, v))
    task_info: Dict[str, Dict[str, Any]] = {}
    for tk, vs in by_task.items():
        recs = [v["rec"] for _, v in vs if v["rec"]]
        cur = [r for r in recs if r["current"] == 1]
        pick = max(cur or recs, key=lambda r: r["updated_at"] or "") if recs else None
        task_info[tk] = {
            "group": pick["task_group_name"] if pick and pick["task_group_name"] else NO_AGENT_TASK,
            "gorder": (pick["task_group_order"] or "") if pick else "~",
            "seq": pick["task_seq"] if pick else 999.0,
            "vdate": max((r["updated_at"] for r in cur), default=None) if cur else None,
        }
    for tk in by_task:
        tasks.setdefault(tk, _Agg())  # zero-run tasks still get a row

    # Group aggs rebuilt from lines so per-run min/avg/max stay exact (not averaged averages).
    groups = {g: _Agg() for g in {i["group"] for i in task_info.values()}}
    for (tk, _), v in ver.items():
        for _, _, ln in v["lines"]:
            groups[task_info[tk]["group"]].add(ln)

    # Candidate validity per (task, version, candidate); only versions with a real agent_task row are scoreable.
    cache: Dict[str, Any] = {"view": {}, "agent": {}, "rubric": {}}
    cvalid: Dict[Tuple[str, str, str], Tuple[Optional[bool], str]] = {}
    vp: Dict[Tuple[str, str], List[Optional[bool]]] = {}  # roll-up inputs per version / task / group
    tp: Dict[str, List[Optional[bool]]] = {}
    gp: Dict[str, List[Optional[bool]]] = {}
    for (tk, label), v in ver.items():
        for cand in v["cands"]:
            res = _candidate_valid(v["rec"], cand, tk, cache) if v["rec"] and cand != "(none)" else (None, "")
            cvalid[(tk, label, cand)] = res
            vp.setdefault((tk, label), []).append(res[0])
            tp.setdefault(tk, []).append(res[0])
            gp.setdefault(task_info[tk]["group"], []).append(res[0])

    rows_out: List[Dict[str, Any]] = []
    lines_only = isinstance(lines, (tuple, list))

    def node(id_: str, parent: Optional[str], level: str, label: str, agg: _Agg, has_children: bool, **extra: Any) -> None:
        if lines_only and level != "line":  # single-candidate line fetch: skip the tree, keep the payload small
            return
        row = {"id": id_, "parent": parent, "level": level, "label": label, "has_children": has_children,
               "task_group": None, "task_key": None, "version": None, "candidate_id": None, "batch_id": None,
               "status": None, "valid": None, "valid_note": None, "version_date": None, "current": None}
        row.update(agg.row())
        row.update(extra)
        rows_out.append(row)

    node("T", None, "total", "ALL TASKS", total, bool(groups), valid=_ratio([x[0] for x in cvalid.values()]))
    for g in sorted(groups, key=lambda g: (min((i["gorder"] for i in task_info.values() if i["group"] == g), default=""), g)):
        gid = f"G|{g}"
        gtasks = [tk for tk, i in task_info.items() if i["group"] == g]
        node(gid, "T", "group", g, groups[g], bool(gtasks), task_group=g,
             valid=_ratio(gp.get(g, [])))
        for tk in sorted(gtasks, key=lambda k: (task_info[k]["seq"], k)):
            info, kid = task_info[tk], f"K|{tk}"
            node(kid, gid, "task", tk, tasks[tk], True, task_group=g, task_key=tk,
                 valid=_ratio(tp.get(tk, [])),
                 version_date=info["vdate"])
            for label, v in sorted(by_task[tk], key=lambda lv: lv[0], reverse=True):
                vid, rec = f"V|{tk}|{label}", v["rec"]
                node(vid, kid, "version", label, v["agg"], bool(v["cands"]), task_group=g, task_key=tk, version=label,
                     valid=_ratio(vp.get((tk, label), [])),
                     version_date=rec["updated_at"] if rec else None,
                     current=bool(rec and rec["current"] == 1))
                for cand in sorted(v["cands"]):
                    cid = f"C|{tk}|{label}|{cand}"
                    node(cid, vid, "candidate", cand, v["cands"][cand], True, task_group=g, task_key=tk,
                         version=label, candidate_id=cand,
                         valid=cvalid[(tk, label, cand)][0], valid_note=cvalid[(tk, label, cand)][1])
                    want = lines == "all" or (isinstance(lines, (tuple, list)) and tuple(lines) == (tk, label, cand))
                    if not want:
                        continue
                    for c2, led, ln in v["lines"]:
                        if c2 != cand:
                            continue
                        node(f"L|{led['batch_id']}", cid, "line", led["batch_id"], _Agg().add(ln), False,
                             task_group=g, task_key=tk, version=label, candidate_id=cand,
                             batch_id=led["batch_id"], status=led["status"])
    return {"rows": rows_out, "meta": {"current_only": current_only}}
