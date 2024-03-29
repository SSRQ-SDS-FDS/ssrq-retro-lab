from collections import namedtuple
from typing import TypedDict

from result import Err, Ok, Result, is_err
from typeguard import typechecked

from ssrq_retro_lab.config import ZG_DATA_ROOT
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.parser.xml_toc_parser import VolumeEntry, parse_xml_toc
from ssrq_retro_lab.pipeline.pdf import extraction
from ssrq_retro_lab.repository.reader import PDFReader, XMLReader
from pydantic import BaseModel


class ExtractionInput(BaseModel):
    article_number: int


VolumeInfo = namedtuple("VolumeInfo", ["pdf_path", "toc_path"])


class TextExtractionResult(TypedDict):
    entry: VolumeEntry
    pages: tuple[str, ...]


class TextExtractor(Component):
    _allowed_retries = 0
    _name = "TextExtractor"
    _repeat_previous = False

    ZG_VOLUMES = {
        1: VolumeInfo(
            ZG_DATA_ROOT / "pdf" / "ZG_1.1.pdf",
            ZG_DATA_ROOT / "toc" / "ZG_1-1.xml",
        ),
        2: VolumeInfo(
            ZG_DATA_ROOT / "pdf" / "ZG_1.2.pdf",
            ZG_DATA_ROOT / "toc" / "ZG_1-2.xml",
        ),
    }
    ZG_ARTICLE_THRESHOLD = 1142

    @typechecked
    def invoke(
        self, extraction_input: ExtractionInput
    ) -> Result[TextExtractionResult, ComponentError]:
        volume_info = self._map_article_number_to_volume(
            extraction_input.article_number
        )
        xml_toc_infos = parse_xml_toc(
            XMLReader(volume_info.toc_path).read(), volume_info.pdf_path
        )

        if is_err(xml_toc_infos):
            return Err(ComponentError(xml_toc_infos.unwrap_err().message))

        entry = xml_toc_infos.unwrap().get_entry(extraction_input.article_number)

        if is_err(entry):
            return Err(ComponentError(entry.unwrap_err().message))

        unwrapped_entry = entry.unwrap()

        pdf = PDFReader(volume_info.pdf_path).read()

        return Ok(
            TextExtractionResult(
                entry=unwrapped_entry,
                pages=extraction.extract_pages(
                    pdf=pdf, toc=xml_toc_infos.unwrap(), entry=unwrapped_entry
                ),
            )
        )

    @typechecked
    def _map_article_number_to_volume(self, article_number: int) -> VolumeInfo:
        return (
            self.ZG_VOLUMES[1]
            if article_number < self.ZG_ARTICLE_THRESHOLD
            else self.ZG_VOLUMES[2]
        )
