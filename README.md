# AARC Annotation Framework for AI-Assisted Mediation

**COSI 115b — Fundamentals of NLP II | Final Project**
**Track:** Research | **Focus:** Data

This project investigates whether AARC deficit labels — Acknowledgement, Agency, Reciprocity, Clarity — correlate meaningfully with friction signals in conflict dialogues, and whether grounding intervention motivation in AARC theory produces a richer reward signal than friction scores alone. The core contribution is a turn-level annotation schema, a synthetic dialogue corpus, and a gold-annotated dataset evaluated for inter-annotator agreement against multiple LLM annotators.

---

## Repository Structure

```
.
├── scripts/              # Pipeline scripts (run in order below)
├── src/fpo_mediation/    # Core library modules
├── data/                 # Corpus and annotation files (generated)
├── docs/                 # Project documentation and reports
├── tests/                # Test suite
├── pyproject.toml        # Package definition and dependencies
└── .env                  # API keys (not tracked)
```

---

## Setup

**Requirements:** Python 3.11+

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the package and its dependencies:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   GROQ_API_KEY=gsk_...    # optional, for Groq-hosted models
   ```

---

## Reproducing the Main Results

The pipeline has four stages. Run them in sequence from the project root.

> `data/personas.json`, `data/scenarios.json`, and `data/stylistics_profiles.json` are pre-generated and committed to the repository — no generation step is needed for these files.

### Stage 1 — Generate the synthetic corpus

```bash
# Plan the corpus (enumerate scenario × persona × stylistics configs)
python3 scripts/plan_corpus.py --write

# Generate dialogues for all planned configs
python3 scripts/generate_corpus.py

# Optional: preview a transcript
python3 scripts/render.py --index 0
```

Output: `data/corpus.jsonl` — the full synthetic dialogue corpus.

### Stage 2 — Gold annotation (human-in-the-loop)

```bash
# Review and label turns interactively
python3 scripts/annotate.py

# Check annotation progress
python3 scripts/annotate.py --list
```

Launches an interactive terminal session for turn-level AARC deficit labeling. For each turn, displays the 7-turn context window alongside any LLM pre-annotation, then prompts to accept or override. Output: `data/gold_annotations.jsonl`.

### Stage 3 — Silver annotation (LLM at scale)

```bash
# Default: Claude Sonnet-4-6
python3 scripts/silver_annotate.py

# With OpenAI
python3 scripts/silver_annotate.py --provider gpt --model gpt-4o

# Check progress
python3 scripts/silver_annotate.py --list
```

Annotates all remaining turns not covered by `gold_annotations.jsonl`. Output: `data/silver_annotations.jsonl`.

**Optional — DSPy-optimized annotation:**

```bash
# Optimize a DSPy annotator on the gold set (saves timestamped program file)
python3 scripts/optimize_dspy.py --auto medium

# Run silver pass using the optimized program
python3 scripts/silver_annotate.py --provider dspy \
    --program-path data/dspy_program_<timestamp>.json
```

For A/G/R-only annotation (Clarity excluded — see known limitations):

```bash
python3 scripts/optimize_dspy_ara.py --auto medium
python3 scripts/silver_annotate.py --provider dspy-ara \
    --program-path data/dspy_program_ara_<timestamp>.json
```

### Stage 4 — Inter-annotator agreement

```bash
python3 scripts/iaa.py \
    --human data/gold_annotations.jsonl \
    --llm data/claude_annotations.jsonl \
    --llm-name "Claude Sonnet-4-6"
```

Computes Cohen's Kappa, observed agreement, positive rates, and Krippendorff's Alpha per AARC component. Writes a timestamped markdown report to `docs/reports/`.

---

## Key Results

IAA results (human gold vs. Claude Sonnet pre-annotation, N=140 turns):

| Component       | Cohen's κ | Observed Agreement |
|-----------------|-----------|--------------------|
| Acknowledgement | 0.62      | 84.3%              |
| Agency          | 0.58      | 82.1%              |
| Reciprocity     | 0.71      | 88.6%              |
| Clarity         | 0.39      | 80.0%              |

Clarity shows the weakest agreement and a systematic over-labeling pattern (LLM positive rate 21.4% vs. 15.7% gold baseline), indicating a taxonomy grounding problem addressed in `FPO-aq6`.

To reproduce these numbers, run the IAA script against the committed annotation files:

```bash
python3 scripts/iaa.py \
    --human data/gold_annotations.jsonl \
    --llm data/claude_annotations.jsonl \
    --llm-name "Claude Sonnet-4-6"
```

### Boundary case review

During gold annotation, turns flagged as boundary cases (ambiguous or cross-component) can be compiled into a review document for closer inspection:

```bash
# All boundary-flagged turns
python3 scripts/boundary_review.py

# Filter to a specific component
python3 scripts/boundary_review.py --component clarity

# Write to a custom path
python3 scripts/boundary_review.py --output docs/reports/boundary_review.md
```

The output is a markdown document showing, for each flagged turn: the 7-turn context window and human gold labels. LLM pre-annotation labels and rationale are shown alongside if `data/pre_annotations.jsonl` is present. Useful for refining taxonomy boundary definitions.

---

## Running the Tests

```bash
# Full suite
pytest tests/

# By category
pytest tests/unit/
pytest tests/validation/
pytest tests/deliverables/

# Skip slow GPU tests
pytest tests/ -m "not slow"

# Live API tests (requires keys in .env)
RUN_LIVE_API_TESTS=1 pytest tests/integration/
```

---

## Data Files

| File | Description |
|------|-------------|
| `data/corpus.jsonl` | Synthetic dialogue corpus (scenario × persona × stylistics) |
| `data/gold_annotations.jsonl` | Human gold labels (140 turns, 4 AARC components) |
| `data/claude_annotations.jsonl` | Claude Sonnet-4-6 pre-annotations (used for IAA) |
| `data/gpt_annotations.jsonl` | GPT pre-annotations (used for IAA) |
| `data/silver_annotations.jsonl` | Full silver annotation pass output |
| `data/personas.json` | Persona library (9 conflict style dimensions) |
| `data/scenarios.json` | Scenario library |
| `data/stylistics_profiles.json` | Stylistics profiles (register, formality, and communication style variants) |

---

## Project Report

The `docs/reports/` directory contains a self-contained HTML report (`report.html`) that visualises the session-by-session change and decision log, including decisions made per session and cumulative hours worked.

To view it, serve the `docs/` directory locally:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000/reports/report.html](http://localhost:8000/reports/report.html) in a browser. The report loads `reports/change_and_decision_log.jsonl` and renders a session timeline and decision summaries.

---

## Position Paper

`position_paper.md` is the theoretical and methodological foundation for this project. It covers:

- **Motivation** — why content-only AI dialogue systems fall into the "content trap" identified in conflict resolution theory, and why pre-mediation assistance requires a different architecture
- **CPRI and AARC frameworks** — the four conflict dimensions (Content, Relationship, Process, Identity) and the four turn-level deficit labels (Acknowledgement, Agency, Reciprocity, Clarity) that ground the annotation schema
- **FPO integration** — how AARC deficit labels extend the FPO friction functional as a richer reward signal
- **Corpus construction** — persona library design, scenario selection, stylistics profiles, and dialogue generation methodology
- **Annotation methodology** — the gold annotation procedure, LLM pre-annotation strategy, IAA results, and DSPy prompt optimization
- **Training and evaluation plan** — reward model architecture, pairwise preference construction, and ablation design

### Bibliography

Sources cited in the position paper are indexed in [`docs/bibliography/index.md`](docs/bibliography/index.md), which lists all 44 entries with author, year, and their specific role in the project argument. Each entry links to a file in `docs/bibliography/` containing the full APA citation and a project-relevance note.

---

## AARC Taxonomy and DSPy Programs

### Taxonomy

The full operationalized annotation taxonomy is in [`docs/aarc_taxonomy.md`](docs/aarc_taxonomy.md) (v5.3). It defines the four deficit components as turn-level annotation targets:

- **Acknowledgement** — unmet need for the speaker's concerns or emotional state to be registered
- **Agency** — reduced sense of autonomy, choice, or efficacy within the interaction
- **Reciprocity** — asymmetry in how obligations, effort, or standing are distributed between parties
- **Clarity** — communicative opacity: ambiguity, vagueness, or frame mismatch that impedes shared understanding

For each component the taxonomy specifies: deficit signals, diagnostic lead-up patterns across the context window, repair indicators (absence-of-deficit markers), boundary cases and discriminators between adjacent components, and worked examples. A diagnostic priority ordering (Acknowledgement → Agency → Reciprocity → Clarity) governs co-occurrence cases.

### DSPy Programs

Optimized DSPy annotators are saved to `data/` as timestamped JSON files and are not overwritten by subsequent runs:

| File pattern | Covers | Optimized on |
|---|---|---|
| `dspy_program_YYYYMMDD_HHMMSS.json` | All four AARC components (A/G/R/C) | 140-turn gold set, recall-weighted metric |
| `dspy_program_ara_YYYYMMDD_HHMMSS.json` | A/G/R only (Clarity excluded) | 140-turn gold set, recall-weighted metric |

The ARA variant was introduced after Clarity IAA fell below threshold; it prevents Clarity over-labeling from degrading the signal on the three better-grounded components. Pass the relevant file to `silver_annotate.py` via `--program-path`.

---

## Known Limitations

- **Clarity taxonomy**: Clarity IAA (κ=0.39) is substantially below the other three components. The taxonomy definition is under revision (see `scripts/boundary_review.py` for flagged cases).
- **Synthetic corpus**: All dialogues are LLM-generated. Naturalistic validation against real conflict transcripts is not yet complete.
- **Reward model**: Training a reward model on the pairwise preference pairs derived from this corpus is planned as future work; it is not included in this submission.
