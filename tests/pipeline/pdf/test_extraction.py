from parsel import Selector
from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.pdf.extraction import extract_pages
from ssrq_retro_lab.repository.reader import PDFReader


def test_extract_pages():
    path = ZG_DATA_ROOT / "pdf" / "ZG_1.1.pdf"
    pdf = PDFReader(path).read()

    pages = extract_pages(pdf, (70, 75))

    assert len(pages) == 6

    for page in pages:
        assert Selector(page, type="xml").xpath("./p/ancestor::div").get() is not None
