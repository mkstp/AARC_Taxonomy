---
name: code-scaffold
description: Generate a Technical Design Document and Testing Framework from project planning files. Use this skill when the user wants to add a code-based scaffold to a project. From a charter, create a technical design document, set up a testing framework, generate architecture diagrams, or produce module specifications from requirements. Trigger whenever you see project_charter.md, deliverables.md, or the user mentions "scaffold," "TDD," "technical design," "test framework," "technical planning," or wants to turn planning documents into code-ready specifications.
---

# Skill: Code Scaffold

Generate a Technical Design Document and Testing Framework from project planning files.

## Purpose

This skill bridges the gap between project planning and implementation by:
1. Transforming abstract requirements into concrete technical specifications
2. Creating a testing framework with full traceability to requirements
3. Producing implementation-ready module designs

## Triggers

Use this skill when the user wants to:
- Create a technical design document from a project charter
- Set up a testing framework for a new project
- Scaffold a project from charter + deliverables files
- Generate architecture, modules, and tests from requirements
- Turn planning documents into implementation specifications

## Required Inputs

The following files must exist and be populated in the project:

| File | Purpose | Key Elements |
|------|---------|--------------|
| `docs/project_charter.md` | Overarching objective, scope, validation conditions | VC-NNN identifiers |
| `docs/deliverables.md` | Discrete outputs with justifications | DEL-NNN identifiers |

## Outputs

This skill produces three linked artifacts:

### 1. Technical Design Document (`docs/technical_design_document.md`)
- System architecture overview with Mermaid diagram
- Module descriptions (MOD-NNN) mapped to deliverables
- Data flow diagrams (Mermaid)
- Data structures with field specifications
- Database schema (conditional — include only if project requires persistence)
- Traceability matrix

### 2. Testing Framework (`tests/`)
- `manifest.json` — traceability map linking tests to VCs, DELs, and MODs
- `validation/` — tests derived from validation conditions
- `deliverables/` — tests verifying deliverable outputs
- `unit/` — module-level tests
- `integration/` — cross-module tests

### 3. Requirements List (`docs/requirements.md`)
- Language-agnostic dependency list with justifications
- Grouped by category (core, testing, development)

---

## Procedure

### Phase 1: Precondition Check

Before reading anything, verify the inputs are ready:

1. Check that `docs/project_charter.md` contains at least one VC-NNN entry
2. Check that `docs/deliverables.md` contains at least one DEL-NNN entry

**If either file is missing populated entries:**

> "The [charter / deliverables file] doesn't have any [validation conditions / deliverables] defined yet. The scaffold needs these to generate meaningful output. Please populate them and re-run `/code-scaffold`."

Stop here. Do not proceed.

**If both files are populated**, continue to Phase 2.

---

### Phase 2: Parse Inputs

1. **Read `docs/project_charter.md`.** Extract:
   - Project name (from title)
   - Overarching objective
   - Scope commitments (in-scope and out-of-scope)
   - Validation conditions: ID, assertion, applies_to, check_method

2. **Read `docs/deliverables.md`.** Extract:
   - Deliverable entries: DEL-NNN, name, description, justification

3. **Build traceability mapping:**
   - Which validation conditions apply to which deliverables
   - Flag any orphaned VCs (conditions that don't apply to any deliverable)

---

### Phase 3: Propose Architecture and Confirm

Before generating any files, present the proposed design to the user for confirmation:

> "Here's the proposed architecture before I generate the files:
>
> **Modules:**
> - MOD-001 `[Name]` — [purpose], implements DEL-001
> - MOD-002 `[Name]` — [purpose], implements DEL-002
> - ...
>
> **Traceability:**
> - DEL-001 ← validated by VC-001, VC-002
> - DEL-002 ← validated by VC-003
>
> **Orphaned VCs (if any):** [list or "none"]
>
> Does this look right? Confirm to proceed, or let me know what to adjust."

Wait for the user to confirm or amend before generating any files.

---

### Phase 4: Generate Technical Design Document

Follow the schema in `res/schemas/technical_design_document.md`.

#### 4.1 System Architecture
- Propose a high-level architecture based on deliverables and scope
- Identify major subsystems or layers
- Create a Mermaid `graph TD` diagram showing components and their relationships
- Document key design decisions with rationale

#### 4.2 Module Descriptions
- Create one primary module (MOD-NNN) per deliverable
- Add supporting modules as needed (utilities, shared services, adapters)
- For each module, specify:
  - **Name:** Concrete, descriptive (e.g., `InputParser`, `ReportGenerator`)
  - **Implements:** Link to DEL-NNN
  - **Purpose:** What this module does
  - **Public Interface:** Key functions with signatures (param types, return types)
  - **Dependencies:** Other modules (internal) and libraries (external)
  - **Validated by:** Which VC-NNN conditions this module must satisfy

#### 4.3 Data Flow Diagrams
- Create Mermaid `flowchart LR` showing:
  - Inputs → Processing stages → Outputs
  - Module interactions
  - External system boundaries (clearly marked)
- Include a flow description table: Flow ID, Source, Destination, Data Type, Trigger

#### 4.4 Data Structures
- Define core data types/models (DS-NNN)
- For each structure:
  - Fields with types and constraints
  - Which modules produce/consume it
- Use language-agnostic type names (string, integer, boolean, list, map)

#### 4.5 Database Schema (Conditional)
- **Include only if** deliverables or scope imply persistence (e.g., "store," "persist," "database," "save user data")
- Create Mermaid `erDiagram` showing entities and relationships
- Define tables with columns, types, and constraints

#### 4.6 Traceability Matrix
- Table showing: Deliverable → Modules → Validation Conditions
- Ensures nothing is orphaned

---

### Phase 4b: Traceability Checkpoint

Before proceeding to test generation, present the traceability matrix from the TDD to the user:

> "Here's the traceability matrix from the design document:
>
> | Deliverable | Modules | Validation Conditions |
> |-------------|---------|----------------------|
> | DEL-NNN [name] | MOD-NNN, ... | VC-NNN, ... |
> | ...
>
> This is the key structural output of the design — everything from here depends on it. Does this look right? Confirm to proceed to test generation, or let me know what to adjust."

Wait for the user to confirm or amend before proceeding.

---

### Phase 5: Language Prompt

Before generating the testing framework, ask:

> "What language is this project implemented in? This determines the test stub syntax. (e.g., Python, TypeScript, Go — default is Python if unspecified)"

Wait for the answer. Use it in Phase 6.

---

### Phase 6: Generate Requirements List and Testing Framework

These two outputs are independent and should be generated in parallel where possible (e.g., delegated to subagents).

#### 6.1 Requirements List (`docs/requirements.md`)

Follow the schema in `res/schemas/requirements.md`.

1. Based on modules and their stated dependencies, list required libraries
2. Group into categories:
   - **Core:** Runtime dependencies
   - **Testing:** Test frameworks, mocking libraries
   - **Development:** Linters, formatters, build tools
3. Include justification for each dependency
4. Note any version constraints or compatibility considerations

#### 6.2 Testing Framework (`tests/`)

**Directory structure:**
```
tests/
├── manifest.json
├── README.md
├── conftest.py          # or language-equivalent setup file
├── validation/
│   └── test_vcNNN_*.py
├── deliverables/
│   └── test_delNNN_*.py
├── unit/
│   └── test_modulename.py
└── integration/
    └── test_integration_*.py
```

**Generate `manifest.json`** — follow the schema in `res/schemas/test_manifest.json`:
- List all validation conditions with linked deliverables, check method classification (`automated`, `manual`, `hybrid`), and test file paths
- List all deliverables with existence and functionality tests
- List all modules with unit test paths
- Build traceability reverse-lookup (DEL → VCs and tests)
- Generate manual checklist for non-automated checks

**Generate test stubs** — follow the template in `res/schemas/test_stub.md`. Use the language confirmed in Phase 5. For each test file:
- **Docstring:** Link to VC-NNN / DEL-NNN / MOD-NNN
- **Imports:** Placeholder for test framework and module under test
- **Fixtures:** Skeleton for test data setup
- **Test functions:** Named `test_[condition]_[expected_outcome]`, Given/When/Then docstring, Arrange/Act/Assert skeleton, `assert False, "Not implemented"` placeholder

**Generate `tests/README.md`** — copy `res/schemas/tests_README.md` to `tests/README.md`, then patch in the actual language and test runner command confirmed in Phase 5.

---

### Phase 7: Convergence Check

Before declaring the skill complete, verify that the parallel outputs from Phase 6 are mutually consistent:

- Every external dependency named in `docs/requirements.md` is referenced by at least one module in the TDD
- Every module in the TDD has a corresponding unit test file in `manifest.json`
- Every VC-NNN in the charter appears in `manifest.json` with a test file or manual checklist entry
- The language used in test stubs matches the language confirmed in Phase 5

If any inconsistency is found, resolve it before proceeding to the quality checklist.

---

## Quality Checks

Before completing, verify:

- [ ] Every DEL-NNN has at least one associated module
- [ ] Every DEL-NNN has at least one test
- [ ] Every VC-NNN has at least one test (or manual checklist item if check_method is manual)
- [ ] Every MOD-NNN in the TDD has a unit test file
- [ ] Manifest traceability is bidirectional
- [ ] Mermaid diagrams use valid syntax
- [ ] No orphaned validation conditions
- [ ] Requirements list covers all external dependencies mentioned in modules

---

## Schemas

Reference these templates when generating outputs:

| Schema | Location | Purpose |
|--------|----------|---------|
| Technical Design Document | `res/schemas/technical_design_document.md` | TDD structure and format |
| Requirements | `res/schemas/requirements.md` | Dependency list format |
| Test Manifest | `res/schemas/test_manifest.json` | Traceability manifest structure |
| Test Stub | `res/schemas/test_stub.md` | Individual test file template |

---

## Notes

- **Language agnosticism:** The TDD and requirements list are language-agnostic. Test stubs use the language confirmed in Phase 5.
- **Iteration:** This skill produces a first-pass scaffold. Expect the user to refine module interfaces and test implementations.
- **Scope creep:** If parsing reveals gaps (e.g., a VC references a DEL that doesn't exist), flag it to the user rather than inventing content.
