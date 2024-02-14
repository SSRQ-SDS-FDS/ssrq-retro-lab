from ssrq_retro_lab.pipeline.components.protocol import Component
from result import is_ok, is_err
from ssrq_retro_lab.pipeline.components.text_extractor import TextExtractor


def test_text_extractor_implements_protocol():
    assert isinstance(TextExtractor, Component)


def test_text_extractor_succeeds_for_existing_article():
    result = TextExtractor().invoke(777)

    assert is_ok(result)


def test_text_extractor_fails_for_non_existing_article():
    result = TextExtractor().invoke(999999)

    assert is_err(result)
