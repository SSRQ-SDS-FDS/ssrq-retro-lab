import pytest
from parsel import Selector
from result import is_ok

from ssrq_retro_lab.pipeline.components.html_wrangler import HTMLWrangler
from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.text_classifier import (
    StructuredArticle,
    TextClassifier,
)
from ssrq_retro_lab.pipeline.components.text_extractor import (
    ExtractionInput,
    TextExtractor,
)
from ssrq_retro_lab.validate.general import calc_ml_metrics


def test_text_classifier_implements_component_protocol():
    assert isinstance(TextClassifier, Component)


@pytest.mark.depends_on_openai
def test_text_classifier_accuracy():
    paragraphs = [
        '<p style="top:100.3pt;left:98.5pt;line-height:10.0pt"><i><span style="font-family:Times New Roman,serif;font-size:10.0pt">Ratsherren von Zug:</span></i><span style="font-family:Times New Roman,serif;font-size:10.0pt"> Wann nun fürhin einer gen Steinhußen welle </span></p>',
        '<p style="top:139.1pt;left:98.9pt;line-height:10.0pt"><span style="font-family:Times New Roman,serif;font-size:10.0pt">einer dar weit ziechenn und den ein gmeind nit weit und aber minen</span></p>',
        '<p style="top:152.1pt;left:87.1pt;line-height:10.0pt"><span style="font-family:Times New Roman,serif;font-size:10.0pt">5 herren gefiel, mögend sy ein gmeind wol heißen, inn under inen zuo </span></p>',
        '<p style="top:219.3pt;left:98.8pt;line-height:8.0pt"><i><span style="font-family:Times New Roman,serif;font-size:8.0pt">BAZug A  39.26.0 fol. 108 r.</span></i></p>',
    ]

    html_result = (
        HTMLWrangler()
        .invoke(TextExtractor().invoke(ExtractionInput(1639, 361, 362)).unwrap())
        .unwrap()
    )

    html_result["article"] = tuple(Selector(p, type="xml") for p in paragraphs)

    result = TextClassifier().invoke(html_result)

    assert is_ok(result)

    structured_article = result.unwrap()

    assert isinstance(structured_article, StructuredArticle)

    assert structured_article.article_number == 1639

    expected_predictions = [3, 1, 1]
    predictions = [
        len(structured_article.text),
        len(structured_article.summary),
        len(structured_article.references),
    ]

    accuracy, _ = calc_ml_metrics(expected_predictions, predictions)

    assert accuracy > 0.9


def test_is_real_title():
    real_title = "Einzugstaxe."
    paragraph = Selector(
        '<p style="top:100.3pt;left:98.5pt;line-height:10.0pt"><i><span style="font-family:Times New Roman,serif;font-size:10.0pt">Ratsherren von Zug:</span></i><span style="font-family:Times New Roman,serif;font-size:10.0pt"> Wann nun fürhin einer gen Steinhußen welle </span></p>',
        type="xml",
    )

    assert (
        TextClassifier._is_real_title(
            1639, paragraph.get(), real_title, "Ratsherren von Zug:"
        )
        is False
    )
