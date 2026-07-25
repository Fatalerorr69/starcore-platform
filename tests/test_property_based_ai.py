"""
Property-Based Tests — AI Generator

Verifies structural invariants for _strip_code_fences and
BlueprintGenerationError that must hold for all valid inputs.

The existing test_property_based.py already covers:
  - idempotence (500 examples)
  - ```yaml fence unwrapping
  - plain ``` fence unwrapping
  - noop on backtick-free text

This file adds complementary properties not yet covered there.
"""

from __future__ import annotations

from ai.generator import BlueprintGenerationError, _strip_code_fences
from hypothesis import given, settings
from hypothesis import strategies as st

# ── _strip_code_fences: additional structural properties ───────────────────────


@given(
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=200,
    )
)
def test_strip_code_fences_unwraps_yml_fence(inner: str) -> None:
    """```yml\\n<content>\\n``` (yml variant) unwraps identically to the yaml variant."""
    assert _strip_code_fences(f"```yml\n{inner}\n```") == inner.strip()


@given(st.text())
@settings(max_examples=500)
def test_strip_code_fences_output_never_has_leading_or_trailing_whitespace(
    text: str,
) -> None:
    """_strip_code_fences always returns a fully-stripped string for any input."""
    result = _strip_code_fences(text)
    assert result == result.strip()


@given(st.text())
@settings(max_examples=500)
def test_strip_code_fences_output_never_longer_than_input(text: str) -> None:
    """The output is never longer than the input — fences can only be removed, not added."""
    assert len(_strip_code_fences(text)) <= len(text)


@given(st.text(alphabet=" \t\n\r"))
def test_strip_code_fences_whitespace_only_input_returns_empty(text: str) -> None:
    """Any whitespace-only input collapses to the empty string."""
    assert _strip_code_fences(text) == ""


@given(
    lang=st.sampled_from(["yaml", "yml", ""]),
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=200,
    ),
)
def test_strip_code_fences_fence_only_block_returns_empty_when_inner_blank(
    lang: str, inner: str
) -> None:
    """A fenced block whose inner content is all whitespace produces an empty string."""
    if inner.strip():
        return  # skip non-empty inner content — this property is about blank content
    tag = lang if lang else ""
    text = f"```{tag}\n{inner}\n```"
    assert _strip_code_fences(text) == ""


@given(
    prefix=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=1,
        max_size=30,
    )
)
def test_strip_code_fences_inline_fence_not_at_line_start_is_preserved(
    prefix: str,
) -> None:
    """A ``` marker that is NOT at the start of a line is left in place.

    The regex uses MULTILINE mode where ^ anchors to the start of each
    line. A backtick sequence embedded mid-line after a non-empty prefix
    does not match ^, so it must survive the substitution unchanged.
    """
    text = f"{prefix}```yaml"
    result = _strip_code_fences(text)
    assert "```yaml" in result


@given(
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=200,
    )
)
def test_strip_code_fences_content_outside_fences_is_preserved(inner: str) -> None:
    """Content that contains no fence markers reaches the output unchanged (modulo strip)."""
    assert _strip_code_fences(inner) == inner.strip()


@given(
    before=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=100,
    ),
    after=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=100,
    ),
    inner=st.text(
        alphabet=st.characters(blacklist_characters="`"),
        max_size=100,
    ),
)
def test_strip_code_fences_content_before_and_after_fence_block_preserved(
    before: str, after: str, inner: str
) -> None:
    """Text before an opening fence and after a closing fence survives the substitution."""
    text = f"{before}\n```yaml\n{inner}\n```\n{after}"
    result = _strip_code_fences(text)
    if before.strip():
        assert before.strip() in result
    if after.strip():
        assert after.strip() in result


# ── BlueprintGenerationError properties ───────────────────────────────────────


@given(msg=st.text(max_size=200))
def test_blueprint_generation_error_preserves_message(msg: str) -> None:
    """The exception message is identical to the string passed to the constructor."""
    exc = BlueprintGenerationError(msg)
    assert str(exc) == msg


@given(
    parts=st.lists(st.text(max_size=50), min_size=1, max_size=4),
)
def test_blueprint_generation_error_is_catchable_as_exception(parts: list[str]) -> None:
    """BlueprintGenerationError can always be caught as a plain Exception."""
    msg = " | ".join(parts)
    caught = False
    try:
        raise BlueprintGenerationError(msg)
    except Exception:
        caught = True
    assert caught


@given(msg=st.text(max_size=200))
def test_blueprint_generation_error_chaining_preserves_cause(msg: str) -> None:
    """When raised with 'from exc', __cause__ is set correctly."""
    cause = ValueError("root cause")
    try:
        raise BlueprintGenerationError(msg) from cause
    except BlueprintGenerationError as exc:
        assert exc.__cause__ is cause
        assert str(exc) == msg
