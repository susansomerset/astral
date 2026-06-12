# Unified assignment — issue fan-out (Astral Artifacts)

Issue-only dependency view (no function-level bullets). Read top-to-bottom; deeper indent means downstream.

Owner colors: <span style="color:#5E6AD2"><strong>Ada</strong></span>, <span style="color:#26B5CE"><strong>Hedy</strong></span>, <span style="color:#BB87FC"><strong>Katherine</strong></span>, <span style="color:#F2994A"><strong>Susan</strong></span>, <span style="color:#636e72"><strong>Ada+Hedy</strong></span>.

Use `Owner: PARENT>CHILD` notation for split epics.

## Current parent/child splits in Linear

| Parent | Child ownership |
|---|---|
| **AST-300** | `Ada: AST-300>AST-370` · `Hedy: AST-300>AST-371` |
| **AST-301** | `Ada: AST-301>AST-368` · `Hedy: AST-301>AST-369` |
| **AST-305** | `Ada: AST-305>AST-361` · `Katherine: AST-305>AST-363` |
| **AST-306** | `Ada: AST-306>AST-362` · `Katherine: AST-306>AST-364` |
| **AST-310** | `Ada: AST-310>AST-365` · `Katherine: AST-310>AST-366` · `Hedy: AST-310>AST-367` |

---

## Fan-out tree (by blockers)

### <span style="color:#5E6AD2"><strong>AST-296</strong></span> lands and opens first wave
- <span style="color:#BB87FC"><strong>AST-297</strong></span>
- <span style="color:#26B5CE"><strong>AST-309</strong></span>
- <span style="color:#5E6AD2"><strong>AST-361</strong></span> → <span style="color:#BB87FC"><strong>AST-363</strong></span>
- <span style="color:#5E6AD2"><strong>AST-362</strong></span> → <span style="color:#BB87FC"><strong>AST-364</strong></span>
- <span style="color:#636e72"><strong>AST-300</strong></span> (parent)
- <span style="color:#636e72"><strong>AST-301</strong></span> (parent)

### <span style="color:#5E6AD2"><strong>AST-304</strong></span> lands and opens chain work
- <span style="color:#5E6AD2"><strong>AST-303</strong></span> (also needs **AST-362**)
- <span style="color:#5E6AD2"><strong>AST-365</strong></span>
- <span style="color:#636e72"><strong>AST-300</strong></span>
- <span style="color:#636e72"><strong>AST-301</strong></span>

### <span style="color:#26B5CE"><strong>AST-302</strong></span> lands and opens state consumers
- <span style="color:#26B5CE"><strong>AST-311</strong></span>
- <span style="color:#636e72"><strong>AST-300</strong></span>
- <span style="color:#636e72"><strong>AST-301</strong></span>
- <span style="color:#BB87FC"><strong>AST-307</strong></span>

### <span style="color:#26B5CE"><strong>AST-309</strong></span> shape path
- <span style="color:#26B5CE"><strong>AST-294</strong></span> (also needs **AST-295**, **AST-296**)
  - <span style="color:#26B5CE"><strong>AST-298</strong></span>
  - <span style="color:#26B5CE"><strong>AST-367</strong></span>
  - <span style="color:#BB87FC"><strong>AST-307</strong></span>
- <span style="color:#636e72"><strong>AST-301</strong></span>
- <span style="color:#BB87FC"><strong>AST-307</strong></span>

### <span style="color:#636e72"><strong>AST-300</strong></span> parent closes when both children close
- `Ada: AST-300>AST-370`
- `Hedy: AST-300>AST-371`
- then unlock/complete <span style="color:#636e72"><strong>AST-301</strong></span>

### <span style="color:#636e72"><strong>AST-301</strong></span> parent closes when both children close
- `Ada: AST-301>AST-368`
- `Hedy: AST-301>AST-369`
- plus dependency on **AST-310 scope** and related soft/process links (**299**, **313**)

### AST-310 scope closes when all three children close
- `Ada: AST-310>AST-365`
- `Katherine: AST-310>AST-366`
- `Hedy: AST-310>AST-367`

### UI closure chain
- <span style="color:#BB87FC"><strong>AST-308</strong></span> → <span style="color:#BB87FC"><strong>AST-307</strong></span>
- <span style="color:#26B5CE"><strong>AST-311</strong></span> + <span style="color:#BB87FC"><strong>AST-307</strong></span> → <span style="color:#BB87FC"><strong>AST-312</strong></span>

### Prompt process gate
- <span style="color:#5E6AD2"><strong>AST-305 scope</strong></span>: **361 + 363**
- <span style="color:#5E6AD2"><strong>AST-306 scope</strong></span>: **362 + 364**
- then <span style="color:#F2994A"><strong>AST-313</strong></span> (process gate on pipeline quality/completion expectations)

---

