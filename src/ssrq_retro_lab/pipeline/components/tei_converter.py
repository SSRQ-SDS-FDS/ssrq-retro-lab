from uuid import uuid4

from loguru import logger
from result import Ok, Result
from spacy.tokens import Doc
from typeguard import typechecked

from ssrq_retro_lab.config import TEI_OUTPUT_DIR
from ssrq_retro_lab.pipeline.components.ocr_corrector import StructuredCorrectedArticle
from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.templates.utils import render_template


class TEIConverter(Component):
    _allowed_retries = 0
    _name = "TEIConverter"
    _repeat_previous = False

    @typechecked
    def invoke(
        self,
        article: tuple[StructuredCorrectedArticle, Doc],
    ) -> Result[tuple[StructuredCorrectedArticle, Doc, str], ComponentError]:
        uuid = str(uuid4())
        tei_xml = render_template(
            template_name="tei_v1.jinja2",
            title=article[0].title,
            uuid=uuid,
            doc=article[1],
        )

        logger.debug(
            f"Created TEI XML for article with number {article[0].article_number}:\n {tei_xml}"
        )

        self._write_tei_based_on_uuid(tei_xml, uuid)

        return Ok((article[0], article[1], tei_xml))

    def _write_tei_based_on_uuid(self, tei_xml: str, uuid: str) -> None:
        if not TEI_OUTPUT_DIR.exists():
            TEI_OUTPUT_DIR.mkdir(parents=True)

        with open(TEI_OUTPUT_DIR / f"{uuid}.xml", "w") as file:
            file.write(tei_xml)
            logger.debug(f"TEI XML written to {TEI_OUTPUT_DIR / f'{uuid}.xml'}")
