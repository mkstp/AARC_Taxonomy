---
name: init-project
description: Initialize a new project — creates Project Charter, Background, and Deliverables files. Aliases: 'start new project', 'begin project'.
---

# SKILL: Initialize Project

## Trigger Conditions

Activate when the user: says "/init-project," "init project," "start new project," "initialize project," or asks to set up project documentation from scratch.

---

## Procedure

### Phase 0: Guard Check

Before doing anything, check whether the `.beads/` directory already exists in the project root.

**If it exists:**

> "This project has already been initialized. Re-initializing would overwrite existing documents and reset the issue tracker. Are you sure you want to continue? (yes/no)"

Wait for explicit confirmation. If the user does not confirm, stop here.

**If it does not exist**, continue to Phase 1.

---

### Phase 1: Intake

Gather the minimum information needed to produce meaningful initial documents. Ask:

> "Before I create the project files, I need a few details:
> 1. **Project name** — what should this project be called?
> 2. **Objective** — in one or two sentences, what is this project trying to achieve?"

Wait for the user's response. Do not proceed to Phase 2 until both answers are provided.

---

### Phase 2: Populate Project Artifacts

The stub files already exist in `docs/` — do not recreate them. Make targeted edits in place using the intake answers from Phase 1:

**`docs/project_charter.md`:**
- Replace `[Project Name]` in the title with the project name provided
- Replace the Overarching Objective placeholder with the objective provided

All other placeholder text remains for the user to populate collaboratively over time. `docs/background.md`, `docs/deliverables.md`, and `docs/reports/change_and_decision_log.jsonl` require no edits at init.

---

### Phase 3: Initialize Beads Issue Tracker

First, verify that `bd` is available:

```bash
bd --version
```

**If `bd` is not found:** surface the install instruction to the user and stop Phase 3 explicitly:

> "`bd` (beads) is not installed. Install it before proceeding: [beads install instructions]. Re-run `/init-project` once installed."

Do not proceed to Phase 4 if `bd` is unavailable.

**If `bd` is available**, run `bd init --stealth` in the project root to create the Beads database at `.beads/`. Refer to the **Outstanding Issues** schema (`res/schemas/outstanding_issues.md`) for CLI usage and conventions.

After init, run `bd setup claude` to configure Beads for Claude Code workflows.

---

### Phase 4: Create Standard Beads Issues

These issues are open at the start of every project. Run the standard issues script:

```bash
bash res/init_issues.sh
```

This creates the four standard issues — Conceptual Grounding, Define Success Criteria, Define Project Deliverables, and Define Technical Implementation — with their standard notes.

---

### Phase 5: Confirm and Handoff

Confirm all files were created and Beads was initialized. Present a brief summary:

> "Project initialized. Created:
> - `docs/project_charter.md` — objective and scope (placeholders remain)
> - `docs/background.md` — background scaffold
> - `docs/deliverables.md` — deliverables scaffold
> - `docs/reports/change_and_decision_log.jsonl` — empty log, ready for EOS
> - `.beads/` — issue tracker with 4 standard issues
>
> **Suggested next steps:**
> 1. Begin Conceptual Grounding — populate `docs/background.md` and flesh out the charter incrementally
> 2. Define deliverables — populate `docs/deliverables.md` as scope becomes clear
> 3. Once charter and deliverables are mature, run `/code-scaffold` to generate the technical design document and testing framework"

---
