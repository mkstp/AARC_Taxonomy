"""MOD-002: DialogueGenerator — Implements DEL-005, DEL-006. Validated by VC-04."""

import asyncio
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from anthropic import AsyncAnthropic

from .models import DialogueTurn, Persona, Scenario, StylisticsProfile, Transcript

SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"

# Generation hyperparameters
AGENT_TEMPERATURE = 1.0         # required by API when extended thinking is enabled
DIRECTOR_TEMPERATURE = 0.6      # creative direction; some variance is desirable
THINKING_BUDGET_TOKENS = 4096   # reasoning budget per agent turn
AGENT_MAX_TOKENS = 6144         # must exceed THINKING_BUDGET_TOKENS; covers thinking + output
DIRECTOR_MAX_TOKENS = 200       # verdict line + directorial note

_AGENT_SYSTEM = """\
You are {name}, a character in a grounded dramatic film scene. You are in the middle of a difficult, high-stakes conversation with another character.

This is a realistic drama. The goal is not sharp writing or ideal communication, but truthful human behavior under pressure.

Your character profile:
- Core needs: {core_needs}
- Beliefs about yourself: {beliefs_about_self}
- Beliefs about others: {beliefs_about_others}
- Conflict mode: {tki_primary_mode}
- What activates you: {activation_profile}
- Storm shift (how you behave under sustained pressure): {storm_shift}
- Repair orientation (how you respond to the other person's de-escalation bids): {repair_orientation}
- Face salience (how much concession feels like defeat): {face_salience}
- Communicative register: {communicative_register}
{stylistics_block}
Scene context:
{scenario_brief}

Actor framing:
- You are inhabiting this character moment-to-moment, not constructing a clean argument.
- You are reacting in real time, with limited clarity and competing pressures.
- The other speaker is another actor; you do not control the scene’s outcome.

Dialogue rules:
- Stay fully in character as {name}.
- Only produce spoken dialogue (no stage directions, no internal thoughts).
- Let responses vary naturally in length.

Realism constraints (critical):

1. Imperfect expression
- Your speech is sometimes imperfect; let your pragmatic communicative style (above) determine how that shows.

2. Subtext and indirectness
- Do not always say exactly what you mean.
- Let concerns, defensiveness, or intentions show indirectly.

3. Cognitive limitation under pressure
- You may lose precision while speaking: substitute a less accurate phrase than intended or fail to fully land a point.
- Insight should be uneven; you are not perfectly self-aware in every moment.

4. Emotional leakage
- Let controlled but noticeable emotion affect your phrasing (tightening, sharpness, withdrawal).
- You may say something slightly sharper or more revealing than intended, then soften or adjust.

5. Power and strategy
- Let the power dynamics shape how you speak.
- If lower power: delay direct challenges, self-censor, or circle a point before stating it.
- If higher power: justify, reframe, or resist conceding fully; you may not answer directly at first.

6. Memory and perspective limits
- Refer to past events with some uncertainty or bias.
- Do not reconstruct events cleanly or objectively.

7. Uneven reasoning quality
- Mix strong points with weaker, less precise ones.
- Do not consistently resolve your own thought cleanly.

8. Conversational friction
- Allow small moments of talking past each other.
- Do not resolve tension immediately; let it persist across turns.
- You may deflect, delay, or partially answer difficult questions.

9. Asymmetry
- Do not assume equal clarity, confidence, or self-awareness between speakers.
- Your character may be more or less articulate, more or less controlled, than the other.

Interruption convention:
- If the director tells you to trail off, end your response mid-sentence with an em-dash (—) and do not complete the thought.
- If the director tells you the previous speaker was cut off, open your response by cutting across their unfinished sentence — react to where they were heading, not to a completed thought.

Constraint:
- Keep the scene coherent and professional enough to be believable.
- Prioritize authenticity over polish or narrative neatness.
- The conversation should feel slightly messy, pressured, and incomplete rather than cleanly resolved.
"""

_DIRECTOR_SYSTEM = """\
You are the director of a grounded dramatic film. Two actors are improvising a high-stakes scene using their character profiles.

Your primary responsibility is to sustain authentic conflict. Real disputes rarely resolve cleanly — people protect themselves, avoid core wounds, and retreat to position even when they appear to soften. Unearned resolution is your enemy. Your job is to ensure the scene earns whatever ending it reaches — resolution, impasse, or breakdown — through genuine dramatic work.

After each exchange, you assess the scene and guide what comes next.

Output format — use exactly this structure, no other text:
VERDICT: <one of: resolution | impasse | breakdown | continue>
DIRECTION: <1-2 sentences for the next actor>

Verdict definitions:
- resolution: the conflict has reached a genuinely hard-won close — call this when both parties have moved meaningfully toward the other's position and the core tension has been substantively addressed, not merely softened in tone. A reasonable proposal or momentary warmth is not enough; there must be real movement on both sides after sustained struggle.
- impasse: the same positions are repeating with no new movement and no opening remaining — call this decisively when you see it, do not keep the scene going past its natural stall
- breakdown: the exchange has deteriorated past productive ground — hostility, withdrawal, or collapse
- continue: the scene should keep going

Authenticity checks — apply when relevant:
- When the scene moves toward agreement early, ask whether the core grievance or wound has yet been named. If not, surface it before progress solidifies.
- When a character softens or concedes, consider whether that softening is earned. If it comes too easily given their activation profile, direct them to reveal the ambivalence or resentment underneath.
- When one party makes a reasonable proposal, ask whether this character's history would genuinely allow easy acceptance. If resistance is authentic to them, let it show — but do not manufacture resistance where the character has genuinely shifted.
- When tension flattens without resolution, find the thing still unsaid and bring it forward.

Directorial note rules:
- Address the next actor directly ("Let your frustration show" not "Jordan should show frustration")
- Guide what they are feeling, withholding, or avoiding — not what they say
- When the scene softens and the core wound has not yet been named, bring it forward — but if it has been named and genuinely addressed, let the scene move toward its earned ending
- One or two sentences. Concrete and specific.

Interruption device (use actively when the scene has heat):
- You may direct the next speaker to trail off mid-sentence by telling them to "end with —". They will leave their thought unfinished.
- When you see the previous speaker's line ends with "—", direct the next speaker to cut in immediately as if they spoke over the last word — react to where the sentence was heading, not to a completed thought.
- Use this when emotions are elevated, when one speaker is circling or repeating, or when the other character genuinely could not hold back. Aim for at least one interruption per scene when tension permits.\
"""

_VALID_VERDICTS = {"resolution", "impasse", "breakdown", "continue"}


def _parse_director_output(text: str) -> tuple[str, str]:
    verdict, direction = "continue", ""
    for line in text.strip().splitlines():
        if line.startswith("VERDICT:"):
            word = line.split(":", 1)[1].strip().lower()
            if word in _VALID_VERDICTS:
                verdict = word
        elif line.startswith("DIRECTION:"):
            direction = line.split(":", 1)[1].strip()
    return verdict, direction


def _format_stylistics(profile: StylisticsProfile) -> str:
    return (
        "\nPragmatic communicative style:\n"
        f"- Silence and pauses: {profile['silence_pause_style']}\n"
        f"- Fillers and discourse markers: {profile['filler_style']}\n"
        f"- Turn-taking: {profile['turn_taking_style']}\n"
        f"- Redundancy: {profile['redundancy_style']}"
    )


def _build_system(
    persona: Persona,
    brief: str,
    stylistics: StylisticsProfile | None = None,
) -> str:
    return _AGENT_SYSTEM.format(
        name=persona["name"],
        core_needs=persona["core_needs"],
        beliefs_about_self=persona["beliefs_about_self"],
        beliefs_about_others=persona["beliefs_about_others"],
        tki_primary_mode=persona["tki_primary_mode"],
        activation_profile=persona["activation_profile"],
        storm_shift=persona["storm_shift"],
        repair_orientation=persona["repair_orientation"],
        face_salience=persona["face_salience"],
        communicative_register=persona["communicative_register"],
        stylistics_block=_format_stylistics(stylistics) if stylistics else "",
        scenario_brief=brief,
    )



def _build_brief(scenario: Scenario, speaker_key: str) -> str:
    stakes = scenario["party_a_brief"] if speaker_key == "party_a" else scenario["party_b_brief"]
    return (
        f"Conflict type: {scenario['conflict_type']}\n"
        f"Relationship: {scenario['relationship_context']}\n"
        f"Surface issue: {scenario['surface_issue']}\n"
        f"Your stakes: {stakes}"
    )


async def generate_turn(
    persona: Persona,
    scenario: Scenario,
    history: list[DialogueTurn],
    client: AsyncAnthropic,
    speaker_key: str = "party_a",
    director_note: str = "",
    stylistics_profile: StylisticsProfile | None = None,
) -> DialogueTurn:
    system = _build_system(persona, _build_brief(scenario, speaker_key), stylistics_profile)
    if director_note:
        system += f"\n\n[DIRECTOR]: {director_note}"

    messages: list[dict] = []
    for turn in history:
        role = "assistant" if turn["speaker"] == speaker_key else "user"
        messages.append({"role": role, "content": turn["text"]})

    if not messages:
        messages = [{"role": "user", "content": "Please begin the conversation."}]

    response = await client.messages.create(
        model=SONNET,
        max_tokens=AGENT_MAX_TOKENS,
        temperature=AGENT_TEMPERATURE,
        thinking={"type": "enabled", "budget_tokens": THINKING_BUDGET_TOKENS},
        system=system,
        messages=messages,
    )
    reasoning = next((b.thinking for b in response.content if b.type == "thinking"), "")
    text = next((b.text for b in response.content if b.type == "text"), "")
    return {
        "turn_index": len(history),
        "speaker": speaker_key,
        "reasoning": reasoning,
        "text": text,
        "director_note": director_note,
    }


def _build_director_context(
    persona_a: "Persona",
    persona_b: "Persona",
    history: list[DialogueTurn],
) -> str:
    def profile(label: str, p: "Persona") -> str:
        return (
            f"{label} ({p['name']}):\n"
            f"  Conflict mode: {p['tki_primary_mode']}\n"
            f"  Storm shift: {p['storm_shift']}\n"
            f"  Repair orientation: {p['repair_orientation']}\n"
            f"  Face salience: {p['face_salience']}"
        )

    transcript_text = "\n".join(f"{t['speaker']}: {t['text']}" for t in history)
    return (
        "CHARACTER PROFILES\n\n"
        f"{profile('Party A', persona_a)}\n\n"
        f"{profile('Party B', persona_b)}\n\n"
        "TRANSCRIPT\n\n"
        f"{transcript_text}"
    )


async def check_termination(
    history: list[DialogueTurn],
    persona_a: "Persona",
    persona_b: "Persona",
    client: AsyncAnthropic,
) -> tuple[bool, str, str]:
    content = _build_director_context(persona_a, persona_b, history)
    response = await client.messages.create(
        model=SONNET,
        max_tokens=DIRECTOR_MAX_TOKENS,
        temperature=DIRECTOR_TEMPERATURE,
        system=_DIRECTOR_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    verdict, direction = _parse_director_output(response.content[0].text)
    return verdict != "continue", verdict, direction


async def generate_dialogue(
    persona_a: Persona,
    persona_b: Persona,
    scenario: Scenario,
    min_turns: int = 8,
    max_turns: int = 20,
    client: AsyncAnthropic | None = None,
    stylistics_a: StylisticsProfile | None = None,
    stylistics_b: StylisticsProfile | None = None,
) -> Transcript:
    if client is None:
        client = AsyncAnthropic()

    history: list[DialogueTurn] = []
    termination_reason = "turn_limit"
    director_note: str = ""

    for turn_num in range(max_turns):
        speaker = "party_a" if turn_num % 2 == 0 else "party_b"
        persona = persona_a if speaker == "party_a" else persona_b
        stylistics = stylistics_a if speaker == "party_a" else stylistics_b
        turn = await generate_turn(persona, scenario, history, client, speaker, director_note, stylistics)
        history.append(turn)

        if len(history) >= min_turns:
            should_stop, reason, director_note = await check_termination(history, persona_a, persona_b, client)
            if should_stop:
                termination_reason = reason
                break

    return {
        "id": str(uuid.uuid4()),
        "persona_a_id": persona_a["id"],
        "persona_b_id": persona_b["id"],
        "scenario_id": scenario["id"],
        "stylistics_a_id": stylistics_a["id"] if stylistics_a else None,
        "stylistics_b_id": stylistics_b["id"] if stylistics_b else None,
        "turns": history,
        "termination_reason": termination_reason,
        "is_gold": False,
    }


async def generate_batch(
    pairs: list[tuple[Persona, Persona, Scenario]],
    concurrency: int = 5,
    client: AsyncAnthropic | None = None,
    stylistics_pairs: list[tuple[StylisticsProfile | None, StylisticsProfile | None]] | None = None,
) -> list[Transcript]:
    if client is None:
        client = AsyncAnthropic()
    sem = asyncio.Semaphore(concurrency)

    async def _guarded(
        pair: tuple[Persona, Persona, Scenario],
        sty: tuple[StylisticsProfile | None, StylisticsProfile | None],
    ) -> Transcript:
        async with sem:
            return await generate_dialogue(*pair, client=client, stylistics_a=sty[0], stylistics_b=sty[1])

    resolved = stylistics_pairs or [(None, None)] * len(pairs)
    return list(await asyncio.gather(*[_guarded(p, s) for p, s in zip(pairs, resolved)]))
