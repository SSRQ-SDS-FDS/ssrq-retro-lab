from loguru import logger
from parsel import Selector
from result import Err, Ok, Result, is_err
from typeguard import typechecked

from ssrq_retro_lab.pipeline.components.protocol import Component, ComponentError
from ssrq_retro_lab.pipeline.components.text_extractor import TextExtractionResult
from ssrq_retro_lab.pipeline.parser.html_to_article import (
    collect_article_nodes_from_pages,
    remove_header_from_pages,
)


class HTMLTextExtractionResult(TextExtractionResult):
    article: tuple[Selector, ...]


class HTMLWrangler(Component):
    _allowed_retries = 0
    _name = "HTMLWrangler"
    _repeat_previous = False

    @typechecked
    def invoke(
        self, text: TextExtractionResult
    ) -> Result[HTMLTextExtractionResult, ComponentError]:
        pages_without_header = remove_header_from_pages(pages=text["pages"])

        if is_err(pages_without_header):
            return Err(ComponentError(pages_without_header.unwrap_err().args[0]))

        text["pages"] = pages_without_header.unwrap()

        logger.debug(
            f"Pages after removing header for article {text['entry'].no}:\n {text['pages']}"
        )

        article_nodes = collect_article_nodes_from_pages(
            text["pages"], text["entry"].no, text["entry"].no + 1
        )

        if is_err(article_nodes):
            return Err(ComponentError(article_nodes.unwrap_err().args[0]))

        article_result = article_nodes.unwrap()

        logger.debug(
            f"Found {len(article_result)} nodes for article {text['entry'].no}."
        )

        return Ok(
            HTMLTextExtractionResult(
                entry=text["entry"], pages=text["pages"], article=article_result
            )
        )
