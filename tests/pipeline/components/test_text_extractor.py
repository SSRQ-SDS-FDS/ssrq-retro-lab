from result import is_err, is_ok

from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.text_extractor import (
    ExtractionInput,
    TextExtractor,
)


def test_text_extractor_implements_protocol():
    assert isinstance(TextExtractor, Component)


def test_text_extractor_succeeds_for_existing_article():
    result = TextExtractor().invoke(ExtractionInput(article_number=1))

    assert is_ok(result)


def test_text_extractor_returns_expected_number_of_pages():
    result = TextExtractor().invoke(ExtractionInput(article_number=793))

    assert is_ok(result)

    text_result = result.unwrap()

    text_result["pages"]

    assert len(text_result["pages"]) == 1


def test_text_extractor_fails_for_non_existing_article():
    result = TextExtractor().invoke(ExtractionInput(article_number=999999))

    assert is_err(result)
