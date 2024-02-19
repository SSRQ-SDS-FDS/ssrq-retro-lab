import pytest
from ssrq_retro_lab.pipeline.components.ocr_corrector import (
    CorrectedOCRText,
    StructuredCorrectedArticle,
)


@pytest.fixture
def corrected_article() -> StructuredCorrectedArticle:
    text = [
        "Die drei Brüder Hans, Ulrich und Heinrich Bütler von Hünenberg",
        "und ihr Vetter, Welti Bütler von Stadelmatt, haben laut Kaufbrief",
        "vom 17. Januar 1414 die Güter und Rechte des Junkers Hartmann",
        "von Hünenberg an sich gebracht und auch den anderen Leuten des",
        "Twings zu Hünenberg Anteil an den Rechtsamen und Nutzungen zu-",
        "erkannt.",
    ]
    return StructuredCorrectedArticle(
        article_number=1556,
        date="1416-01-21",
        corrected_references=CorrectedOCRText(text=[]),
        references=[],
        corrected_summary=CorrectedOCRText(text=[]),
        summary=[],
        corrected_text=CorrectedOCRText(text=text),
        text=text,
        title="Anschluß an Zug",
    )
