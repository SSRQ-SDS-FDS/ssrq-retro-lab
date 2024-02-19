import pytest
from parsel import Selector
from result import is_ok
from ssrq_retro_lab.pipeline.components.ner_annotator import NERAnnotator
from ssrq_retro_lab.pipeline.components.ocr_corrector import StructuredCorrectedArticle
from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.tei_converter import TEIConverter


def test_tei_converter_implements_protocol():
    assert isinstance(NERAnnotator, Component)


@pytest.mark.depends_on_openai
def test_tei_conversion(corrected_article: StructuredCorrectedArticle):
    namespaces = {"tei": "http://www.tei-c.org/ns/1.0"}
    result = NERAnnotator().invoke(corrected_article)

    assert is_ok(result)

    tei_conversion_result = TEIConverter().invoke(result.unwrap())

    assert is_ok(tei_conversion_result)

    _, _, tei = tei_conversion_result.unwrap()

    tei_selector = Selector(tei, type="xml")

    title = tei_selector.xpath(
        "//tei:titleStmt/tei:title/text()", namespaces=namespaces
    ).get()

    assert title is not None

    assert title == corrected_article.title

    assert tei_selector.xpath("//tei:body", namespaces=namespaces).get() is not None
