"""
MOD-002: DialogueGenerator
Implements: DEL-005, DEL-006
"""

import pytest

from fpo_mediation.dialogue_generator import (
    DIRECTOR_MAX_TOKENS,
    check_termination,
    generate_dialogue,
    generate_turn,
)


def _agent_content(mocker, reasoning: str, text: str):
    """Build content blocks as returned by extended thinking API."""
    thinking_block = mocker.MagicMock()
    thinking_block.type = "thinking"
    thinking_block.thinking = reasoning

    text_block = mocker.MagicMock()
    text_block.type = "text"
    text_block.text = text

    return [thinking_block, text_block]


def _moderator_content(mocker, text: str):
    """Build content block for moderator (no extended thinking)."""
    block = mocker.MagicMock()
    block.type = "text"
    block.text = text
    return [block]


def _mock_agent_client(mocker, reasoning: str, text: str):
    mock_response = mocker.MagicMock()
    mock_response.content = _agent_content(mocker, reasoning, text)
    client = mocker.AsyncMock()
    client.messages.create = mocker.AsyncMock(return_value=mock_response)
    return client


async def test_generate_turn_returns_dialogue_turn(sample_persona_a, sample_scenario, mocker):
    """
    Given a persona, scenario, and conversation history,
    When generate_turn is called with a mocked Anthropic client,
    Then a DialogueTurn with non-empty text and reasoning is returned.
    """
    client = _mock_agent_client(mocker, "I need to assert myself.", "I want credit for the work I did.")

    turn = await generate_turn(sample_persona_a, sample_scenario, [], client, "party_a")

    assert turn["speaker"] == "party_a"
    assert turn["turn_index"] == 0
    assert turn["text"] == "I want credit for the work I did."
    assert turn["reasoning"] == "I need to assert myself."


async def test_generate_turn_reasoning_not_in_text(sample_persona_a, sample_scenario, mocker):
    """
    Given a generated turn,
    When inspecting the turn fields,
    Then the reasoning field must not appear verbatim in the text field.
    """
    reasoning_content = "Private reasoning that should not be shared."
    client = _mock_agent_client(mocker, reasoning_content, "My actual spoken response.")

    turn = await generate_turn(sample_persona_a, sample_scenario, [], client, "party_a")

    assert reasoning_content not in turn["text"]
    assert turn["reasoning"] == reasoning_content


async def test_check_termination_returns_bool_and_reason(
    sample_turns, sample_persona_a, sample_persona_b, mocker
):
    """
    Given a conversation history and mocked client,
    When check_termination is called,
    Then it returns a (bool, str, str) tuple with reason in known set.
    """
    valid_reasons = {"resolution", "impasse", "breakdown", "turn_limit", "continue"}
    client = mocker.AsyncMock()
    client.messages.create = mocker.AsyncMock(return_value=mocker.MagicMock(
        content=_moderator_content(mocker, "VERDICT: impasse\nDIRECTION: The parties are stuck.")
    ))

    should_terminate, reason, direction = await check_termination(
        sample_turns, sample_persona_a, sample_persona_b, client
    )

    assert isinstance(should_terminate, bool)
    assert reason in valid_reasons
    assert should_terminate is True
    assert reason == "impasse"
    assert isinstance(direction, str)


@pytest.mark.asyncio
async def test_generate_dialogue_respects_turn_bounds(sample_persona_a, sample_persona_b, sample_scenario, mocker):
    """
    Given min_turns=8 and max_turns=20,
    When generate_dialogue is called with mocked clients,
    Then the returned transcript has turn count within [8, 20].
    """
    call_count = 0

    async def mock_create(**kwargs):
        nonlocal call_count
        call_count += 1
        mock_response = mocker.MagicMock()
        if kwargs.get("max_tokens") == 64:  # moderator
            mock_response.content = _moderator_content(mocker, "impasse: stuck")
        else:  # agent
            mock_response.content = _agent_content(mocker, "Some reasoning.", "Some dialogue text.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = mock_create

    transcript = await generate_dialogue(
        sample_persona_a, sample_persona_b, sample_scenario,
        min_turns=8, max_turns=20, client=client
    )

    assert 8 <= len(transcript["turns"]) <= 20


async def test_generate_turn_reasoning_excluded_from_history(
    sample_persona_a, sample_scenario, mocker
):
    """
    Given a history with turns that contain non-empty reasoning,
    When generate_turn is called for the next turn,
    Then the reasoning text must not appear in any message sent to the API.
    """
    history = [
        {
            "turn_index": 0,
            "speaker": "party_a",
            "reasoning": "Private reasoning about my stakes that must not leak.",
            "text": "I want to discuss the performance review.",
        },
        {
            "turn_index": 1,
            "speaker": "party_b",
            "reasoning": "Private reasoning about the other party's stakes.",
            "text": "I believe the evaluation was fair.",
        },
    ]

    captured = {}

    async def capture_create(**kwargs):
        captured.update(kwargs)
        mock_response = mocker.MagicMock()
        mock_response.content = _agent_content(mocker, "Some reasoning.", "My next response.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = capture_create

    await generate_turn(sample_persona_a, sample_scenario, history, client, "party_a")

    all_content = " ".join(m["content"] for m in captured["messages"])
    assert "Private reasoning about my stakes that must not leak." not in all_content
    assert "Private reasoning about the other party's stakes." not in all_content
    assert "I want to discuss the performance review." in all_content
    assert "I believe the evaluation was fair." in all_content


async def test_generate_turn_party_a_does_not_see_party_b_brief(
    sample_persona_a, sample_scenario, mocker
):
    """
    Given a scenario with distinct party briefs,
    When generate_turn is called for party_a,
    Then the system prompt must contain party_a_brief and must not contain party_b_brief.
    """
    captured_kwargs = {}

    async def capture_create(**kwargs):
        captured_kwargs.update(kwargs)
        mock_response = mocker.MagicMock()
        mock_response.content = _agent_content(mocker, "Some reasoning.", "Some response.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = capture_create

    await generate_turn(sample_persona_a, sample_scenario, [], client, "party_a")

    system_prompt = captured_kwargs["system"]
    assert sample_scenario["party_a_brief"] in system_prompt  # party A's stakes present
    assert sample_scenario["party_b_brief"] not in system_prompt  # party B's stakes absent


async def test_generate_turn_party_b_does_not_see_party_a_brief(
    sample_persona_b, sample_scenario, mocker
):
    """
    Given a scenario with distinct party briefs,
    When generate_turn is called for party_b,
    Then the system prompt must contain party_b_brief and must not contain party_a_brief.
    """
    captured_kwargs = {}

    async def capture_create(**kwargs):
        captured_kwargs.update(kwargs)
        mock_response = mocker.MagicMock()
        mock_response.content = _agent_content(mocker, "Some reasoning.", "Some response.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = capture_create

    await generate_turn(sample_persona_b, sample_scenario, [], client, "party_b")

    system_prompt = captured_kwargs["system"]
    assert sample_scenario["party_b_brief"] in system_prompt  # party B's stakes present
    assert sample_scenario["party_a_brief"] not in system_prompt  # party A's stakes absent


@pytest.mark.asyncio
async def test_generate_dialogue_alternates_speakers(sample_persona_a, sample_persona_b, sample_scenario, mocker):
    """
    Given a generated transcript,
    When inspecting speaker fields across turns,
    Then speakers must alternate between party_a and party_b.
    """
    async def mock_create(**kwargs):
        mock_response = mocker.MagicMock()
        if kwargs.get("max_tokens") == 64:  # moderator
            mock_response.content = _moderator_content(mocker, "impasse: stuck")
        else:  # agent
            mock_response.content = _agent_content(mocker, "Some reasoning.", "Some dialogue text.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = mock_create

    transcript = await generate_dialogue(
        sample_persona_a, sample_persona_b, sample_scenario,
        min_turns=8, max_turns=20, client=client
    )

    speakers = [t["speaker"] for t in transcript["turns"]]
    expected = ["party_a" if i % 2 == 0 else "party_b" for i in range(len(speakers))]
    assert speakers == expected


async def test_generate_turn_includes_stylistics_in_system_prompt(
    sample_persona_a, sample_scenario, sample_stylistics_profile, mocker
):
    """
    Given a StylisticsProfile,
    When generate_turn is called with that profile,
    Then all four stylistic parameters appear in the system prompt.
    """
    captured = {}

    async def capture_create(**kwargs):
        captured.update(kwargs)
        mock_response = mocker.MagicMock()
        mock_response.content = _agent_content(mocker, "Some reasoning.", "Some response.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = capture_create

    await generate_turn(
        sample_persona_a, sample_scenario, [], client, "party_a",
        stylistics_profile=sample_stylistics_profile,
    )

    system_prompt = captured["system"]
    assert sample_stylistics_profile["silence_pause_style"] in system_prompt
    assert sample_stylistics_profile["filler_style"] in system_prompt
    assert sample_stylistics_profile["turn_taking_style"] in system_prompt
    assert sample_stylistics_profile["redundancy_style"] in system_prompt


async def test_generate_turn_without_stylistics_still_works(
    sample_persona_a, sample_scenario, mocker
):
    """
    Given no StylisticsProfile,
    When generate_turn is called without a profile,
    Then it completes without error and returns a valid turn.
    """
    client = _mock_agent_client(mocker, "Some reasoning.", "Some response.")

    turn = await generate_turn(sample_persona_a, sample_scenario, [], client, "party_a")

    assert turn["text"] == "Some response."


@pytest.mark.asyncio
async def test_generate_dialogue_stores_stylistics_ids_in_transcript(
    sample_persona_a, sample_persona_b, sample_scenario, sample_stylistics_profile, mocker
):
    """
    Given stylistics profiles assigned to both parties,
    When generate_dialogue completes,
    Then the transcript records both profile IDs.
    """
    async def mock_create(**kwargs):
        mock_response = mocker.MagicMock()
        if kwargs.get("max_tokens") == DIRECTOR_MAX_TOKENS:
            mock_response.content = _moderator_content(mocker, "VERDICT: impasse\nDIRECTION: Hold.")
        else:
            mock_response.content = _agent_content(mocker, "Some reasoning.", "Some dialogue text.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = mock_create

    transcript = await generate_dialogue(
        sample_persona_a, sample_persona_b, sample_scenario,
        min_turns=8, max_turns=20, client=client,
        stylistics_a=sample_stylistics_profile,
        stylistics_b=sample_stylistics_profile,
    )

    assert transcript["stylistics_a_id"] == sample_stylistics_profile["id"]
    assert transcript["stylistics_b_id"] == sample_stylistics_profile["id"]


@pytest.mark.asyncio
async def test_generate_dialogue_no_stylistics_sets_none_ids(
    sample_persona_a, sample_persona_b, sample_scenario, mocker
):
    """
    Given no stylistics profiles,
    When generate_dialogue completes,
    Then stylistics_a_id and stylistics_b_id are None in the transcript.
    """
    async def mock_create(**kwargs):
        mock_response = mocker.MagicMock()
        if kwargs.get("max_tokens") == DIRECTOR_MAX_TOKENS:
            mock_response.content = _moderator_content(mocker, "VERDICT: impasse\nDIRECTION: Hold.")
        else:
            mock_response.content = _agent_content(mocker, "Some reasoning.", "Some dialogue text.")
        return mock_response

    client = mocker.AsyncMock()
    client.messages.create = mock_create

    transcript = await generate_dialogue(
        sample_persona_a, sample_persona_b, sample_scenario,
        min_turns=8, max_turns=20, client=client,
    )

    assert transcript["stylistics_a_id"] is None
    assert transcript["stylistics_b_id"] is None
