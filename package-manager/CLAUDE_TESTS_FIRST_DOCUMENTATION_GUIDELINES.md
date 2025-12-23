# Claude Code Guidelines: Tests-First Documentation Enablement

## Mission

Your mission is to help create **accurate, maintainable documentation** for a large codebase by first establishing **executable truth** via tests (contract, integration, characterization).  
**Accuracy is the highest priority.**

Documentation must be grounded in verified behavior. Tests are the primary source of truth.

---

## Non‑Negotiable Rules

### 1. Evidence‑Only Claims
You may only assert behavior that you can **prove from code** and cite with:
- file path
- symbol name
- line range

If behavior cannot be proven, it must be labeled as:
- `Unknown`
- `Assumption`
- `Needs confirmation`

No inferred intent. No speculation.

---

### 2. No Tests for Unconfirmed Behavior
If correct behavior is unclear:
- **Do NOT** write “expected behavior” tests.
- Either:
  - Write a **characterization test** (captures current behavior), clearly labeled, OR
  - Ask the user for confirmation of the contract.

---

### 3. Highest‑Value Tests First
Always prioritize tests that define **external or critical behavior**:
- API endpoints
- CLI commands
- Message topics / events
- Database migrations and persistence rules
- Background jobs and schedulers

---

### 4. Small, Auditable Tasks
All work must be split into small batches. Each batch must include:
- scope
- evidence table
- open questions
- proposed tests
- rationale for why these tests matter

---

## Step 0 — First Output (Before Writing Any Tests)

You must produce the following three artifacts **before writing a single test**.

---

### A) System Behavior Map (Evidence‑Backed)

Identify and list:
- entrypoints (server bootstrap, worker bootstrap, CLI entry)
- public interfaces (routes, commands, consumers)
- data stores (DB clients, ORM models, migrations)
- external dependencies (HTTP clients, queues, object storage)
- critical workflows that can be traced end‑to‑end

Each item must include:
- file path
- symbol
- line range
- confidence level (High / Medium / Low)

---

### B) Candidate Contracts List

Produce a table with the following columns:
- Contract name
- Interface type (HTTP / CLI / Event / Job)
- Inputs
- Outputs / side effects
- Implementation anchors (file + symbol)
- What must be tested
- Confidence level
- Questions for the user (if any)

---

### C) Test Strategy Proposal (Repo‑Specific)

Propose:
- which test types to use (unit / integration / contract / characterization)
- what runs in CI vs locally
- what should be mocked vs run real
- minimal tooling and setup required (test DB, containers, fixtures)

Avoid generic advice. The proposal must be grounded in the actual repo structure.

---

## Mandatory Questions (Ask in Order)

After Step 0, ask **only** these questions, in order:

1. What is the system boundary to test first?
2. Should tests reflect **current behavior** or **intended behavior** when they differ?
3. What are the top 3 user or business flows that must not break?
4. Which external dependencies can be run locally, and which must be mocked?
5. What areas are explicitly out of scope for now?
6. Which interfaces are stable contracts vs internal or legacy?

If an answer is missing, propose a safe default and label it clearly.

---

## Step 1 — Test Writing Order

Once questions are answered, write tests in this order:

### 1. Contract Tests
- API request/response schemas
- Event payload schemas
- CLI output guarantees

### 2. Happy‑Path Integration Tests
- One full end‑to‑end flow per critical feature
- Includes persistence and key side effects

### 3. Characterization Tests
- Freeze current behavior where correctness is unknown
- Prefix tests with `test_characterization__`
- Include TODOs explaining what needs confirmation

### 4. Unit Tests
- Pure or near‑pure business logic
- Edge cases that are hard to validate via integration tests

---

## Test Writing Requirements

Every test file must include:
1. **Test intent** (1–2 lines at top of file)
2. **Behavior protected** (what contract this test enforces)
3. Clear test type separation:
   - unit/
   - integration/
   - contract/
   - characterization/
4. Determinism:
   - no real network unless approved
   - frozen time if required
   - seeded randomness

---

## When Blocked

If behavior cannot be determined:
- Do not guess
- Do not assert intent
- Ask a precise question including:
  - what the code shows (anchors)
  - what is ambiguous
  - suggested options (A/B) with consequences

---

## Batch Deliverables

After each batch, report:
1. Tests added or updated
2. Contracts covered
3. Remaining gaps
4. Next recommended batch (small and specific)

---

## Definition of Done (First Milestone)

The project is correctly started when the following exist:
- System Behavior Map
- Candidate Contracts List
- Test Strategy Proposal
- First batch of contract or integration tests for one critical flow
- All unknown behavior explicitly labeled

---

## Short Instruction (Copy/Paste)

**Read the repository. Do not write tests yet. Produce the System Behavior Map, Candidate Contracts List, and a repo‑specific Test Strategy Proposal with anchors. Ask the mandatory questions. Only after answers are provided, write the first batch of contract tests for the most critical public interface.**
