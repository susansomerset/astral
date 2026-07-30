# AST-1079 — Unique-contact field contract in config

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1079/unique-contact-field-contract-in-config-verify-unique-contact-info  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1045/verify-unique-contact-info  

**Publish ref (origin):** `sub/AST-1045/AST-1079-unique-contact-field-contract`  
**Parent integration ref:** `ftr/AST-1045-verify-unique-contact-info`

Define the **config vocabulary** for which contact values participate in within-candidate dedupe and cross-candidate uniqueness, plus compare rules (casefold for emails/handles; exact for Slack user ids), as a sibling block next to `CANDIDATE_LOOKUP_CONFIG` so bind/lookup and the future save gate (AST-1080) share one email-path source. This ticket does **not** enforce uniqueness on save, touch Profile/Admin UI, or change the contact library schema.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` after `CANDIDATE_LOOKUP_CONFIG`; module-docstring inventory line; import-time asserts tying email/slack paths to lookup | utils |

---

## Stage 1: Uniqueness field contract in config

**Done when:** `from src.utils.config import CANDIDATE_CONTACT_UNIQUENESS_CONFIG` works; email paths are identical to `CANDIDATE_LOOKUP_CONFIG["email_paths"]` (including transitional `profile.*`); phone / github / linkedin_url / websites / slack_user_id participation and compare modes are readable from the block; no core, data, UI, or enforce logic exists yet.

1. In `src/utils/config.py` module docstring **Config sections** list, add one line (alphabetically near other candidate blocks is fine; place after the `CONTACT_CONFIG` line or next to candidate lookup if that inventory style is used):

```
  CANDIDATE_CONTACT_UNIQUENESS_CONFIG — contact uniqueness / within-candidate dedupe field paths + compare rules (AST-1079; sibling to CANDIDATE_LOOKUP_CONFIG)
```

2. Immediately **after** the existing `CANDIDATE_LOOKUP_CONFIG` block (the dict that ends with `slack_user_id_paths`, currently just above the `CONTACT_CONFIG` comment banner), and **before** the `CONTACT_CONFIG` banner, insert:

```python
# ---------------------------------------------------------------------------
# CANDIDATE_CONTACT_UNIQUENESS_CONFIG: save-gate field contract (AST-1079 / AST-1045).
# Vocabulary only — within-candidate dedupe + cross-candidate collision enforcement
# is AST-1080. Email / slack path tuples must stay aligned with CANDIDATE_LOOKUP_CONFIG.
# ---------------------------------------------------------------------------
CANDIDATE_CONTACT_UNIQUENESS_CONFIG = {
    # Same object as lookup — bind/lookup and uniqueness share one email vocabulary
    # (including transitional profile.* until gone).
    "email_paths": CANDIDATE_LOOKUP_CONFIG["email_paths"],
    # Non-email identity handles under the AST-1014 contact blob.
    "scalar_paths": (
        "contact.phone",
        "contact.github",
        "contact.linkedin_url",
    ),
    # List-valued contact fields: each non-empty entry is one uniqueness token.
    "list_paths": (
        "contact.websites",
    ),
    # Same object as lookup Slack homes (AST-1066 / AST-1068).
    "slack_user_id_paths": CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"],
    # Compare mode per path group. Enforcement (AST-1080) must:
    #   - strip whitespace on all string values before compare
    #   - for "casefold": compare with str.casefold()
    #   - for "exact": compare stripped strings as-is (no casefold)
    #   - skip empty / missing values (not uniqueness tokens)
    "compare": {
        "email": "casefold",
        "scalar": "casefold",
        "list": "casefold",
        "slack_user_id": "exact",
    },
    # Both scopes use the same path set. Semantics of refuse vs collapse are AST-1080
    # (parent OQ: avoid adding the same contact info twice; hard-fail cross-candidate).
    "scopes": (
        "within_candidate",
        "cross_candidate",
    ),
}
```

⚠️ **Decision — sibling block, not a key on `CANDIDATE_LOOKUP_CONFIG`:** Lookup is string→id match homes; uniqueness is save-gate participation + compare modes + list vs scalar shape. A sibling keeps lookup callers unchanged and avoids teaching every lookup reader about save scopes. Email/slack path **objects** are shared so the vocabularies cannot drift.

⚠️ **Decision — “all contact info” = identity handles from parent OQ options:** Parent OQ#1 listed emails / phone / LinkedIn / GitHub / websites and locked “All contact info.” Uniqueness-scoped set is those plus `contact.slack_user_id` (already a lookup identity home). **Not** in the uniqueness set: `location`, `timezone`, `cover_letter_signature`, `cover_letter_signature_image`, `title_patterns`, `reason_codes` — those are contact-blob keys but not identity handles in the OQ list.

⚠️ **Decision — transitional `profile.*` only on emails:** Parent AC#4 / OQ#5 require alignment with `CANDIDATE_LOOKUP_CONFIG` email paths (including transitional `profile.*`). Non-email uniqueness paths are `contact.*` only; do not invent `profile.phone` / `profile.websites` mirrors here.

⚠️ **Decision — compare modes:** Emails/handles use `casefold` (same intent as `CANDIDATE_LOOKUP_CONFIG["match_casefold"] is True`). Slack user ids use `exact` after strip (Slack ids are opaque tokens; do not casefold). Do **not** invent phone digit-normalization or URL canonicalization beyond strip+casefold in this ticket — `normalize_contact_urls` remains library coercion (AST-1014); AST-1080 may call it before uniqueness compare if the save path already does.

3. Immediately after the new block, add import-time asserts (same style as neighboring config asserts):

```python
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_paths"] is CANDIDATE_LOOKUP_CONFIG["email_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["slack_user_id_paths"] is CANDIDATE_LOOKUP_CONFIG["slack_user_id_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["compare"]["email"] == "casefold"
assert CANDIDATE_LOOKUP_CONFIG["match_casefold"] is True  # email uniqueness must stay casefold while lookup is
assert isinstance(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"], tuple) and CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"]
assert isinstance(CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"], tuple) and CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scopes"] == ("within_candidate", "cross_candidate")
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"]:
    assert isinstance(_p, str) and _p.startswith("contact."), _p
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]:
    assert isinstance(_p, str) and _p.startswith("contact."), _p
_contact_key_set = set(CANDIDATE_LIBRARY_CONFIG["contact_keys"])
for _p in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"] + CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"]:
    _key = _p.split(".", 1)[1]
    assert _key in _contact_key_set, _p
for _mode in CANDIDATE_CONTACT_UNIQUENESS_CONFIG["compare"].values():
    assert _mode in ("casefold", "exact"), _mode
```

4. Do **not** edit `src/core/candidate.py`, `src/data/database.py`, UI, or any enforce/dedupe helpers. Do **not** add keys to `CANDIDATE_LOOKUP_CONFIG`. Do **not** change `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`. Do **not** register callers of the new block (AST-1080 owns that).

**Done when (recheck):** In a Python shell from repo root with `PYTHONPATH=.` (or the project’s usual import path):

```python
from src.utils.config import (
    CANDIDATE_CONTACT_UNIQUENESS_CONFIG,
    CANDIDATE_LOOKUP_CONFIG,
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["email_paths"] == (
    "contact.contact_email",
    "contact.reply_email",
    "profile.contact_email",
    "profile.reply_email",
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["scalar_paths"] == (
    "contact.phone",
    "contact.github",
    "contact.linkedin_url",
)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["list_paths"] == ("contact.websites",)
assert CANDIDATE_CONTACT_UNIQUENESS_CONFIG["slack_user_id_paths"] == ("contact.slack_user_id",)
```

---

## Self-Assessment

**Scope:** `minor` — one new utils config block + docstring/asserts; no core/data/UI.

**Conf:** `high` — mirrors `CANDIDATE_LOOKUP_CONFIG` / `CONTACT_CONFIG` sibling pattern; parent OQs lock field set and email alignment; enforce semantics deferred to AST-1080.

**Risk:** `low` — no callers until AST-1080; wrong paths would only misconfigure a future gate, not change runtime behavior in this ticket.

---

## Code Rules check (§8)

| Rule | Result |
|------|--------|
| §1.3 DRY | Email/slack path tuples reused by reference from `CANDIDATE_LOOKUP_CONFIG`; no second hardcoded email list |
| §2.1 config source of truth | New `*_CONFIG` block; literals only; no `os.environ` |
| §1.4 no-hardcoded-sets | Uniqueness participation lives in config for AST-1080 to read |
| §2.4 batch / §2.6 state machine | N/A — config vocabulary only |
| §3.3 imports | No new modules; utils-only change |
| §3.5 naming | `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` matches candidate + concern naming |

No conflicts requiring `conf-!!-NONE`.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-1079 |
| Publish ref | `origin/sub/AST-1045/AST-1079-unique-contact-field-contract` |
| Built | `fb4cd6e02c39ada87e5628f1177739f3cd536d8a` |
| Notes | Stage 1 — `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` sibling to lookup; email/slack path objects shared by identity. |

### Radia — code-rubric.v1

`[code-rubric] revision=1` · **Overall:** DISCUSS (stragglers only; product CLEAN)

**What’s solid**
- Sibling `CANDIDATE_CONTACT_UNIQUENESS_CONFIG` matches plan Stage 1 verbatim: email/slack path objects shared by identity with `CANDIDATE_LOOKUP_CONFIG`; scalar/list paths + compare/scopes as specified; import-time asserts lock alignment and `contact_keys` membership.
- No core/data/UI/enforce creep — AST-1080 boundary held.
- Engineer `code()` touched only `src/utils/config.py`; Betty owns `test()` / `merge-tests`.

**Issues**
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff vs `origin/dev` brings `docs/features/**` + Betty test-tree paths in scope. All three score **conforms** on this diff — no product fix.

**Recommended actions**
- Ada: no code change required for stragglers; proceed `resolve-child` → User Testing unless a discuss thread is opened.
- Full statutes-checked table + Linear comment on AST-1079.
