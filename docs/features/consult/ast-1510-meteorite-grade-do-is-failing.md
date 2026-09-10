# AST-1510 — meteorite_grade_do is failing

<!-- linear-archive: AST-1510 archived 2026-09-09 -->

## Linear archive (AST-1510)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1510/meteorite-grade-do-is-failing  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

# meteorite_grade_do is failing

Log output (2026-08-26 staging batch `meteorite_grade_do-f8e798a5-00d6-404f-b18f-ea3d9a26f176`, candidate somerset):

```
batch finished COMPLETED with errors — processed=11 passed=0 failed=0 errors=11
incomplete grade set -> METEORITE_FAILED_TECHNICAL_DO
missing=['Hands-On Technical Partnership With Engineers']
decoded payload example: 000|AGA5|AIA5|CFB4|DKC3|DSB4|DTB4|RGX0|RRB4|SAB4|SRB4|TPB4|TPB4
(decodes 12 segments; Speaking Truth to Power With Diplomacy appears twice; HT absent)
vector_reviews: all 12 lines parse=fail (bad_line) — e.g. AGRACVE, AIRACVE, TPRACVE
expected feedback codes (11): AG, AI, CF, DK, DS, DT, RG, RR, SA, SR, TP — count=11, no HT
```

## As-is

Susan confirms the root issue: `TP` **is used twice** in the somerset Do rubric code set (two vectors share the two-letter code `TP`, or the prompt/rubric presents `TP` twice). The model emits `TPB4` twice; decode maps both segments to the **same** vector label (`Speaking Truth to Power With Diplomacy`), so `Hands-On Technical Partnership With Engineers` **never appears** in the decoded grade set. Consult apply rejects the batch as incomplete → jobs exhaust retry holding → `METEORITE_FAILED_TECHNICAL_DO`.

**Decode behavior when the same two-letter code appears twice** (Susan's trace question — no repro, code logic only):

1. `_vector_labels_map` (`consult.py`) builds `{code: label}` from live rubric criteria — **one entry per code; if two rubric rows share a code, the later row wins silently** (dict comprehension overwrites).
2. `_decode_payload` (`agent.py`) walks each grade segment in order and **appends** a row `{vector: vector_labels[code], grade, confidence}` — duplicate codes produce **two grade rows with the same vector name**, not two different vectors.
3. `_require_complete_grade_set` (`consult.py`) compares **sets** of vector labels — a duplicate segment does **not** satisfy a second missing rubric vector; the colliding vector's grade is counted once.
4. **Neither duplicate "wins" the other vector's slot** — the vector whose code lost the map (or was never emitted) is simply absent; hydration/scoring never routes a grade to the wrong label unless both labels collapsed to one code in step 1.

Separately, all `vector_reviews` strings fail strict parse (`bad_line`; clarity letter `C` not in A/O/S/R/N) — secondary, does not block the hop.

## To-be

Somerset Do rubric has **unique two-letter codes** for every vector (including Hands-On Technical Partnership With Engineers — not sharing `TP` with Speaking Truth to Power With Diplomacy). `meteorite_grade_do` decodes a complete grade set (one segment per rubric code), applies scored Do pass/fail, and optionally captures vector feedback when the model follows wire format.

## Proposed steps

1. Inspect somerset `rubric_vector` rows for owner `grade_do`: find the duplicate `TP` assignment (which two labels share it; confirm HT's intended code).
2. Reassign codes so every current Do vector has a unique two-letter code (Artifacts save or targeted row fix); verify resolved `{$RUBRIC_VECTORS}` lists each code once.
3. Consider a guard at rubric sync/save or decode time to reject duplicate codes before they reach dispatch (optional hardening — only if Susan wants product enforcement, not just data repair).
4. Re-run somerset `meteorite_grade_do` on staging; confirm jobs score instead of incomplete-grade error.

## Component scope

* `src/core/candidate.py` — modified if adding duplicate-code validation on rubric save/sync — reject or warn when two current `rubric_vector` rows for the same owner share a code.
* `src/core/consult.py` — modified only if hardening `_vector_labels_map` to detect/log duplicate codes instead of silent last-wins (diagnostic).
* `src/core/agent.py` — modified only if decode should fail fast on duplicate codes in one line (optional; data fix may be sufficient).
* **Somerset rubric data** (via Artifacts UI / `rubric_vector` rows) — modified — reassign duplicate `TP` so HT and TP are distinct codes (primary fix if collision is data-only).

## Technical scope

* `src/core/candidate.py`: optional new validation in rubric sync/save path — when building criteria from `rubric_vector` rows, raise or surface duplicate `code` values for one `(candidate_id, task_key)` owner before persist.
* `src/core/consult.py`: optional `_vector_labels_map` change — detect duplicate codes in input list and log/raise Style D detail under `debug=True` instead of silent last-wins overwrite.
* `src/core/agent.py`: optional decode guard — if the same two-char code appears twice in one encoded line, treat as incomplete/retry with explicit duplicate-code detail (AST-1155 retry path).
* **Rubric data**: reassign the colliding vector's code (likely HT vs TP) so `_vector_labels_map` and the model prompt agree on eleven unique codes.

## Ancestor candidates

- [X] AST-723 — Rubric vector read/write cutover (`docs/features/auditor/ast-723-rubric-vector-read-write-cutover.md`) — rubric authority in `rubric_vector` rows + `{$RUBRIC_VECTORS}`; code↔label mapping is the collision surface
- [ ] AST-1283 — Grade_do is erroring (`docs/features/consult/ast-1283-grade-do-is-erroring.md`) — same meteorite_grade_do / somerset failure family
- [ ] AST-1150 — Technical fail for Do prompt (`docs/features/consult/ast-1150-technical-fail-for-do-prompt.md`) — parent epic for rubric completeness + retry policy
- [ ] AST-1154 — Rubric completeness contracts (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`) — prompt requires every rubric code once (does not fix duplicate codes in data)
- [ ] AST-1222 — Meteorite do/get alias seed (`docs/features/meteorite/ast-1222-meteorite-do-get-alias-seed-retarget-dispatch.md`) — `meteorite_grade_do` resolves content from master `grade_do`
- [ ] AST-1269 — UAT alias agent_task rows not seeded (`docs/features/meteorite/ast-1269-uat-alias-agent-task-rows-not-seeded-on-startup.md`) — lower confidence; task is running

### Comments

#### susan — 2026-08-26T23:36:37.608Z
The issue is that TP is used twice.  😞.

Question: When the agent responds with two encoded responses that are duplicate (e.g. "ABA5|DCA5|ABB4" where the first "AB" is "Absolute Binary" and the second "AB" is "About Benefits", which of the two grades gets saved, and does it get saved to the correct place?  No repro options here, just trace the code logic.

---

_Implementation detail may live in git history on `origin/dev`._
