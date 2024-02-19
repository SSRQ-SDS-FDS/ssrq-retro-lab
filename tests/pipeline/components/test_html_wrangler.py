import pytest
from result import is_ok

from ssrq_retro_lab.pipeline.components.html_wrangler import (
    HTMLWrangler,
)
from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.text_extractor import (
    ExtractionInput,
    TextExtractor,
)


def test_html_wrangler_implements_protocol():
    assert isinstance(HTMLWrangler, Component)


@pytest.mark.parametrize(
    ("text_extractor_input", "expected_nodes"),
    [
        (
            ExtractionInput(article_number=793),
            6,
        ),
        (
            ExtractionInput(article_number=599),
            4,
        ),
    ],
)
def test_html_wrangler_returns_expected_nodes_for_article(
    text_extractor_input: ExtractionInput, expected_nodes: int
):
    text_result = TextExtractor().invoke(text_extractor_input).unwrap()

    result = HTMLWrangler().invoke(text_result)

    assert is_ok(result)

    html_result = result.unwrap()

    assert len(html_result["article"]) == expected_nodes
