import pytest
from result import is_ok
from ssrq_retro_lab.pipeline.components.ocr_corrector import OCRCorrector
from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.pipeline.components.text_classifier import StructuredArticle
from ssrq_retro_lab.validate.ocr import calc_error_rate
from ssrq_retro_lab.validate.general import calc_ml_metrics
import numpy as np


def test_ocr_corrector_implements_protocol():
    assert isinstance(OCRCorrector, Component)


@pytest.mark.depends_on_openai
def test_ocr_corrector_corrects_texts():
    input_text = [
        "lange nach ußw ißt u n d t zugidth. Is t der kauff geschehen um b ein h undert und",
        "den eyden, so sy getan habent, aber jeglichem in dem twing ußze-",
    ]
    expected_text = [
        "lange nach ußwißt undt zugidth. Ist der kauff geschehen umb ein hundert und",
        "den eyden, so sy getaͮn habent, aber jeglichem in dem twing ußze-",
    ]

    article = StructuredArticle(
        article_number=1554,
        date="1414-01-17",
        references=[],
        summary=[],
        text=input_text,
        title="Kauf von Hünenberg",
    )

    result = OCRCorrector().invoke(article)

    assert is_ok(result)

    corrected_article = result.unwrap()

    expected_text_list = list(" ".join(expected_text).strip())
    corrected_text_list = list(" ".join(corrected_article.corrected_text.text).strip())

    max_length = max(len(expected_text_list), len(corrected_text_list))

    expected_text_array = np.pad(
        expected_text_list,
        (0, max_length - len(expected_text_list)),
        mode="constant",
        constant_values=" ",
    )
    corrected_text_array = np.pad(
        corrected_text_list,
        (0, max_length - len(corrected_text_list)),
        mode="constant",
        constant_values=" ",
    )

    accuracy, _ = calc_ml_metrics(list(expected_text_array), list(corrected_text_array))

    assert accuracy < 90

    cer, _ = calc_error_rate(
        "\n".join(expected_text), "\n".join(corrected_article.corrected_text.text)
    )

    assert cer < 2.25
