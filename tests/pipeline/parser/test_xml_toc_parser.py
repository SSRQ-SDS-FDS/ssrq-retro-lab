from parsel import Selector
from ssrq_retro_lab.pipeline.parser.xml_toc_parser import (
    _get_volume_meta_infos,
    parse_xml_toc,
    _parse_entry,
    VolumeMeta,
    VolumeEntry,
    XMLToC,
)
from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.repository.reader import XMLReader
from result import is_ok
import pytest


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
