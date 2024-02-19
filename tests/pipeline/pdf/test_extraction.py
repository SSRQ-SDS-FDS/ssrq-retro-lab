from parsel import Selector
import pytest

from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.pdf.extraction import extract_pages
from ssrq_retro_lab.repository.reader import PDFReader, XMLReader
from ssrq_retro_lab.pipeline.parser.xml_toc_parser import parse_xml_toc, XMLToC


@pytest.fixture
def toc():
    path = ZG_DATA_ROOT / "toc" / "ZG_1-1.xml"
    return parse_xml_toc(XMLReader(path).read(), path).unwrap()


@pytest.mark.parametrize(
    ("number, expected_pages"),
    [
        (790, 1),
        (793, 1),
    ],
)
def test_extract_pages(toc: XMLToC, number: int, expected_pages: int):
    path = ZG_DATA_ROOT / "pdf" / "ZG_1.1.pdf"
    pdf = PDFReader(path).read()

    pages = extract_pages(pdf, toc, toc.get_entry(790).unwrap())

    assert len(pages) == expected_pages

    for page in pages:
        assert Selector(page, type="xml").xpath("./p/ancestor::div").get() is not None
