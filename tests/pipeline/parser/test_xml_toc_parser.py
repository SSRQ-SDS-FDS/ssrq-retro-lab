import pytest
from parsel import Selector
from result import is_ok

from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.parser.xml_toc_parser import (
    VolumeEntry,
    VolumeMeta,
    XMLToC,
    _get_volume_meta_infos,
    _parse_entry,
    parse_xml_toc,
    _map_book_pages_to_img,
)
from ssrq_retro_lab.repository.reader import XMLReader


@pytest.fixture
def toc():
    path = ZG_DATA_ROOT / "toc" / "ZG_1-1.xml"
    return XMLReader(path).read()


def test_parse_xml_toc(toc: Selector):
    xml_toc = parse_xml_toc(toc, ZG_DATA_ROOT / "toc" / "ZG_1-1.xml")

    assert is_ok(xml_toc)

    xml_toc_unwrapped = xml_toc.unwrap()

    assert isinstance(xml_toc_unwrapped, XMLToC)
    assert len(xml_toc_unwrapped.entries) == len(
        toc.xpath("//entry[date][not(entry[date])]")
    )


def test_get_volume_meta_infos(toc: Selector):
    volume_meta = _get_volume_meta_infos(toc)

    assert is_ok(volume_meta)

    volume_meta_unwrapped = volume_meta.unwrap()

    assert isinstance(volume_meta_unwrapped, VolumeMeta)
    assert volume_meta_unwrapped.canton == "ZG"
    assert volume_meta_unwrapped.volume == "1.1"
    assert volume_meta_unwrapped.title == "Grund- und Territorialherren. Stadt und Amt"


def test_parse_entry(toc: Selector):
    entry = toc.xpath("//entry[date][no/text() = '777']")[0]

    assert entry is not None
    parsed_entry = _parse_entry(entry, toc)

    assert is_ok(parsed_entry)
    unwrapped_entry = parsed_entry.unwrap()

    assert isinstance(unwrapped_entry, VolumeEntry)
    assert unwrapped_entry.no == 777
    assert unwrapped_entry.title == "Mandat gegen Einbrecher und Diebe."
    assert unwrapped_entry.pages == (476, 477)

    entry = toc.xpath("//entry[date][no/text() = '822']")[1]

    assert entry is not None
    parsed_entry = _parse_entry(entry, toc)

    assert is_ok(parsed_entry)
    unwrapped_entry = parsed_entry.unwrap()

    assert isinstance(unwrapped_entry, VolumeEntry)
    assert unwrapped_entry.no == 822
    assert unwrapped_entry.title == "Korneinfuhr."
    assert unwrapped_entry.pages == (505,)


@pytest.mark.parametrize(
    ("page_number", "img_number"),
    [
        (43, 81),
        (502, 544),
        (483, 525),
    ],
)
def test_map_book_pages_to_img(toc: Selector, page_number: int, img_number: int):
    pages = _map_book_pages_to_img(toc)

    assert is_ok(pages)
    assert pages.unwrap()[page_number] == img_number
