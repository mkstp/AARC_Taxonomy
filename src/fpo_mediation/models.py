from typing import TypedDict


class Persona(TypedDict):
    id: str
    name: str
    core_needs: str
    beliefs_about_self: str
    beliefs_about_others: str
    tki_primary_mode: str
    storm_shift: str
    activation_profile: str
    repair_orientation: str
    face_salience: str
    communicative_register: str


class StylisticsProfile(TypedDict):
    id: str
    label: str
    silence_pause_style: str
    filler_style: str
    turn_taking_style: str
    redundancy_style: str


class Scenario(TypedDict):
    id: str
    conflict_type: str
    relationship_context: str
    surface_issue: str
    party_a_brief: str  # full scenario text shown only to party A
    party_b_brief: str  # full scenario text shown only to party B


class DialogueTurn(TypedDict):
    turn_index: int
    speaker: str  # party_a | party_b
    reasoning: str
    text: str
    director_note: str  # directorial guidance that preceded this turn (empty if none)


class Transcript(TypedDict):
    id: str
    persona_a_id: str
    persona_b_id: str
    scenario_id: str
    stylistics_a_id: str | None
    stylistics_b_id: str | None
    turns: list[DialogueTurn]
    termination_reason: str  # resolution | impasse | breakdown | turn_limit
    is_gold: bool


class DialogueWindow(TypedDict):
    id: str
    transcript_id: str
    window_index: int
    turns: list[DialogueTurn]
    acknowledgement_deficit: bool | None  # None = unannotated
    agency_deficit: bool | None
    reciprocity_deficit: bool | None
    clarity_deficit: bool | None
    is_high_friction: bool  # true if any deficit is True
    rationale: str | None
    annotation_source: str | None  # gold | silver


class GoldAnnotation(TypedDict):
    window_id: str
    acknowledgement_deficit: bool
    agency_deficit: bool
    reciprocity_deficit: bool
    clarity_deficit: bool
    annotator_notes: str
    annotated_by: str  # researcher ID
    annotation_date: str  # ISO 8601


class TurnAnnotation(TypedDict):
    turn_id: str           # "{transcript_id[:8]}-t{turn_index:04d}"
    transcript_id: str
    turn_index: int
    acknowledgement_deficit: bool
    agency_deficit: bool
    reciprocity_deficit: bool
    clarity_deficit: bool
    annotator_notes: str
    annotator_confidence: int  # 1=low, 2=medium, 3=high; default 3
    boundary_case: bool        # flagged by annotator as a boundary case for review
    annotated_by: str
    annotation_date: str   # ISO 8601


class PreAnnotation(TypedDict):
    turn_id: str
    transcript_id: str
    turn_index: int
    acknowledgement_deficit: bool
    agency_deficit: bool
    reciprocity_deficit: bool
    clarity_deficit: bool
    rationale: str         # one-sentence reasoning trace
    confidence: float      # 0.0–1.0, self-reported by model
    model: str
    annotation_date: str   # ISO 8601
