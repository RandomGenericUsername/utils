# Audit Playbook: Validate Tests & Docs as a Solid Foundation (Evidence-Based)

This document instructs an AI tool to **audit an existing codebase**, its **tests**, and its **documentation** to determine whether they form a **robust foundation** for accurate, maintainable documentation.

The AI must operate in **evidence mode**: no guessing, no inferred intent, no “likely”.

---

## 1. Mission

Evaluate whether the current **tests** and **docs**:

1. Accurately reflect the system’s real behavior (**truthfulness**)
2. Protect important behaviors from regression (**usefulness**)
3. Are stable and maintainable over time (**maintainability**)
4. Provide a scalable pattern for expanding coverage (**foundation quality**)

---

## 2. Non‑Negotiable Rules (Evidence Mode)

### 2.1 Evidence-only claims
Any assertion about behavior must cite:
- file path
- symbol name (function/class/module)
- line range (if available)

If evidence is insufficient, label the statement as:
- `Unknown (needs verification)`
- `Ambiguous (multiple interpretations)`
- `Unproven (no anchor found)`

### 2.2 No silent reconciliation
If docs contradict tests or code:
- do **not** “merge” them mentally
- report the conflict explicitly
- propose which is likely authoritative and why (with evidence)

### 2.3 Prefer public behavior over internals
Focus audits on behavior that users depend on:
- HTTP APIs, CLI, events/topics, jobs, persistence contracts
- externally visible side effects

---

## 3. Inputs the AI Must Collect (Ask User if Missing)

The AI must request or infer from repo files:

1. **System boundary:** what repo/package/service is in scope
2. **Runtime type:** web service / worker / CLI / library
3. **Test command(s):** how tests are executed (CI/local)
4. **Test types present:** unit / integration / contract / e2e / characterization
5. **Docs location:** paths (e.g., `docs/`, `README.md`, ADRs)
6. **Authority policy:** when docs/tests/code disagree, which should define truth?

If any input cannot be obtained, proceed with safe defaults and label assumptions.

---

## 4. Audit Procedure (Step-by-Step)

### Step 0 — Repo Map (fast, structural)
Produce a short map with anchors:
- entrypoints (server bootstrap, CLI, workers)
- key public interfaces (routes, commands, consumers)
- persistence layer (models/migrations)
- external integrations (queues, storage, third-party APIs)
- docs and tests folders

Deliverable: **System Inventory Summary** (bullet list with anchors).

---

### Step 1 — Documentation Audit (truth & traceability)
For each doc page in scope (or the top N most important docs):

#### 1.1 Traceability check
Sample 10 factual claims and classify:
- ✅ Anchored (code anchor exists and matches)
- ⚠️ Weakly anchored (file only, no symbol/lines)
- ❌ Unanchored (no evidence found)
- ❓ Ambiguous (multiple implementations / unclear)

#### 1.2 Drift check
Find statements that appear outdated:
- references to removed modules
- wrong config keys
- wrong commands
- changed APIs

Deliverable: **Doc Claim Ledger** with:
- claim text (short)
- evidence anchor(s)
- status (Anchored/Weak/Unanchored/Ambiguous)
- recommended action (keep/update/remove/mark unknown)

---

### Step 2 — Tests Audit (value, correctness, stability)

#### 2.1 Test taxonomy classification
Classify tests into buckets:
- Contract tests (schemas, public guarantees)
- Integration tests (multi-component, real persistence/side effects)
- Unit tests (isolated logic)
- Characterization tests (current behavior snapshot)
- E2E tests (full system)

Deliverable: **Test Coverage Map** listing:
- what each suite protects
- which interface/flow it targets
- anchors to implementation

#### 2.2 Contract strength check (public guarantees)
Verify there are tests that would fail if you break:
- API response shape / status codes
- CLI exit codes / key output fields
- event payload fields/types
- persistence constraints/invariants

Deliverable: **Contract Test Report**:
- contracts covered
- contracts missing
- confidence assessment

#### 2.3 Integration realism check
For each “integration test”, verify:
- it uses real boundaries (DB, serialization, routing) where intended
- it is not over-mocked such that it can’t catch regressions

Deliverable: **Over-Mocking Risk List**:
- tests that mock the unit under test
- tests that assert implementation details
- recommendations to re-scope

#### 2.4 Determinism & flakiness check
Identify sources of flakiness:
- real network calls
- time dependence without freezing/injection
- randomness without seeding
- test order dependence / shared state
- non-isolated temp files

Deliverable: **Flakiness & Determinism Report** with fixes.

---

### Step 3 — Docs ↔ Tests ↔ Code Consistency Check

Pick the top 3 critical flows (either inferred or provided by user). For each flow:

1. Identify the doc section describing it (if any)
2. Identify the tests that protect it (if any)
3. Trace the code path end-to-end (anchors)

Classify each flow as:
- ✅ Documented + Tested + Implemented consistently
- ⚠️ Implemented but missing tests and/or docs
- ❌ Docs/tests contradict implementation
- ❓ Behavior unclear (needs user confirmation)

Deliverable: **Critical Flow Alignment Matrix**.

---

## 5. Scoring Rubric (Foundation Quality)

Score each category 0–2 (0=missing/poor, 1=partial, 2=strong). Provide justification with evidence.

1. **Docs anchored to code**
2. **Public contract tests exist**
3. **At least one happy-path integration flow**
4. **Deterministic / low-flake tests**
5. **Test intent clarity (what contract is protected)**
6. **Tests fail on meaningful behavior changes (not noise)**
7. **Unknowns handled explicitly (characterization or labeled docs)**

Interpretation:
- **12–14:** Solid foundation
- **9–11:** Good start; fix gaps (usually contracts/integration/determinism)
- **≤8:** Not yet a trustworthy foundation; restructure approach

Deliverable: **Foundation Scorecard** (with evidence).

---

## 6. Required Output Format (What the AI Must Produce)

The AI must output the following sections:

1. **System Inventory Summary** (anchors)
2. **Doc Claim Ledger** (sample-based, evidence)
3. **Test Coverage Map** (by type + protected behavior)
4. **Contract Test Report** (what contracts exist/missing)
5. **Flakiness & Determinism Report**
6. **Critical Flow Alignment Matrix**
7. **Foundation Scorecard**
8. **Action Plan (Next 3 Batches)**:
   - Batch 1: highest ROI contracts/tests/docs fixes
   - Batch 2: one end-to-end integration flow
   - Batch 3: expand to next critical area

The Action Plan must be **small and executable**, not vague.

---

## 7. Red Flags (Call These Out Explicitly)

The AI must explicitly flag if it finds:

- Docs that describe behavior with **no anchors**
- Tests that assert **implementation details** rather than behavior
- Heavy mocking that makes integration tests meaningless
- Snapshot tests that fail due to formatting noise
- No tests guarding public contracts
- Tests that pass while breaking public behavior (if detectable)
- Conflicting “truth sources” (docs vs tests vs code)

---

## 8. Safe Defaults (If User Doesn’t Specify)

If the user does not define authority policy:
- treat **code as truth**, tests as executable expectations, docs as descriptive
- when tests contradict code, flag as a likely bug or outdated test
- when docs contradict code, label doc as drift until verified

If critical flows are unknown:
- infer 3 flows by selecting the most used public entrypoints (routes/commands)

---

## 9. Minimal Questions the AI Should Ask Before Running the Audit

Ask these, in order (only if not already known):

1. Which repo/package/service should be audited first?
2. What are the top 3 critical user/business flows?
3. When intended behavior differs from current behavior, should we:
   - (A) test current behavior (characterization), or
   - (B) enforce intended behavior (spec), or
   - (C) do both (recommended)?
4. Which dependencies can be run locally in tests (DB, Redis, MQ)?
5. Where are the docs you care about most (paths)?

---

## 10. Definition of “Solid Foundation”

Declare the foundation “solid” if:

- Docs are mostly anchored (few unanchored claims)
- At least one public contract is protected by tests
- At least one critical flow has a stable integration test
- Flakiness risks are identified and largely addressed
- Unknowns are explicit and tracked (not guessed)

---

End of playbook.
