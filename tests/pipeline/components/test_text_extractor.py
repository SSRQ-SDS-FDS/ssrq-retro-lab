from result import is_err, is_ok

from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.text_extractor import (
    ExtractionInput,
    TextExtractor,
)


def test_text_extractor_implements_protocol():
    assert isinstance(TextExtractor, Component)


def test_text_extractor_succeeds_for_existing_article():
    result = TextExtractor().invoke(ExtractionInput(777, 518, 518))

    assert is_ok(result)


def test_text_extractor_fails_for_non_existing_article():
    result = TextExtractor().invoke(ExtractionInput(999999, 518, 518))

    assert is_err(result)
