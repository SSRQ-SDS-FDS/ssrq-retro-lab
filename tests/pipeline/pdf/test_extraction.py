import pytest
from parsel import Selector
from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.pdf.extraction import _calc_pdf_pages, extract_pages
from ssrq_retro_lab.repository.reader import PDFReader


def test_extract_pages():
    path = ZG_DATA_ROOT / "pdf" / "ZG_1.1.pdf"
    pdf = PDFReader(path).read()

    pages = extract_pages(pdf, (70, 75))

    assert len(pages) == 6

    for page in pages:
        assert Selector(page, type="xml").xpath("./p/ancestor::div").get() is not None


@pytest.mark.parametrize(
    "start_page, end_page, skip_pages, real_start, expected",
    [
        (70, 75, 0, 0, [69, 70, 71, 72, 73, 74]),
        (43, 45, 81, 43, [80, 81, 82]),
        (579, 580, 29, 579, [28, 29]),
    ],
)
def test_calc_pdf_pages(
    start_page: int,
    end_page: int,
    skip_pages: int,
    real_start: int,
    expected: list[int],
):
    pages = _calc_pdf_pages(
        (start_page, end_page), skip_pages=skip_pages, real_start=real_start
    )

    assert list(pages) == expected
