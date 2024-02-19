import pytest
from result import is_ok
from ssrq_retro_lab.pipeline.components.ner_annotator import NERAnnotator
from ssrq_retro_lab.pipeline.components.ocr_corrector import StructuredCorrectedArticle
from ssrq_retro_lab.pipeline.components.protocol import Component
from ssrq_retro_lab.validate.general import calc_ml_metrics


def test_ner_annotator_implements_protocol():
    assert isinstance(NERAnnotator, Component)


@pytest.mark.depends_on_openai
def test_ner_annotator(corrected_article: StructuredCorrectedArticle):
    result = NERAnnotator().invoke(corrected_article)

    assert is_ok(result)

    _, doc = result.unwrap()

    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    places = [ent.text for ent in doc.ents if ent.label_ == "PLACE"]

    expected_persons = [
        "Hans",
        "Ulrich",
        "Heinrich Bütler",
        "Welti Bütler",
        "Junkers Hartmann",
    ]

    expected_places = ["Hünenberg", "Stadelmatt"]

    assert len(doc.ents) > 0

    accuracy_persons, _ = calc_ml_metrics(expected_persons, persons)

    assert accuracy_persons > 0.9

    accuracy_places, _ = calc_ml_metrics(expected_places, places)

    assert accuracy_places > 0.9
