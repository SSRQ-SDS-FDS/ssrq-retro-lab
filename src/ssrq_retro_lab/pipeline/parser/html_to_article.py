import re

from parsel import Selector
from result import Err, Ok, Result


def collect_article_nodes_from_pages(
    pages: tuple[str, ...], current_article_number: int, next_article_number: int | None
) -> Result[tuple[Selector, ...], ValueError]:
    """A naive and AI-free function to extract all
    relevant nodes for a given article (a document).

    Args:
        pages: The pages to extract the article nodes from as HTML export from PyMuPDF.
        current_article_number: The current article number.
        next_article_number: The next article number.

    Returns:
        The article nodes as a tuple of Selector instances. If no article nodes
        are found, a ValueError is returned as an error."""
    result_nodes: list[Selector] = []

    for page in pages:
        page_selector = Selector(text=page, type="xml")

        current_article_is_on_page = bool(
            page_selector.xpath(
                f"//span[contains(., '{current_article_number}.')]"
            ).get()
        )
        next_article_is_on_page = bool(
            page_selector.xpath(f"//span[contains(., '{next_article_number}.')]").get()
        )

        if current_article_is_on_page and next_article_is_on_page:
            result_nodes.extend(
                page_selector.xpath(
                    f"""//p[preceding-sibling::p[span[contains(., '{current_article_number}.')]]
                    or self::p[span[contains(., '{current_article_number}')]]]
                    [following-sibling::p[span[contains(., '{next_article_number}.')]]]
                    [position() < last()]"""
                )
            )
            continue

        if current_article_is_on_page and not next_article_is_on_page:
            result_nodes.extend(
                page_selector.xpath(
                    f"""//p[preceding-sibling::p[span[contains(., '{current_article_number}.')]]
                    or self::p[span[contains(., '{current_article_number}.')]]]"""
                )
            )
            continue

        if not current_article_is_on_page and next_article_is_on_page:
            result_nodes.extend(
                page_selector.xpath(
                    f"//p[following-sibling::p[span[contains(., '{next_article_number}.')]]][position() < last()]"
                )
            )
            continue

        result_nodes.extend(page_selector.xpath("//p"))

    if len(result_nodes) == 0:
        return Err(ValueError("No article nodes found."))

    return Ok(tuple(result_nodes))


def remove_header_from_pages(
    pages: tuple[str, ...], min_top_position: int = 85
) -> Result[tuple[str, ...], ValueError]:
    """A utility function, which cleans the headers (Kopfzeilen) from
    the pages – if present. It uses a hard-coded threshold to determine
    if a paragraph is a header.

    Args:
        pages: The pages to clean. Each page is HTML as a string.
        min_top_position: The minimum top position of a paragraph not to be
            considered a header.

    Returns:
        The cleaned pages. Each page is HTML as a string. If the number of
        cleaned pages is not equal to the number of pages, a ValueError is
        returned as an error.

    """

    cleaned_pages = []

    for p in pages:
        page_selector = Selector(text=p, type="xml")
        for para in page_selector.css("div p[style]"):
            style = para.xpath("@style").get()

            if style is None:
                continue

            if top_value := re.search(r"top:\s*(\d+(?:\.\d+)?)pt", style):
                if float(top_value.group(1)) <= min_top_position:
                    para.drop()

        cleaned_pages.append(page_selector.get())

    if len(cleaned_pages) != len(pages):
        return Err(
            ValueError(
                "The number of cleaned pages is not equal to the number of pages."
            )
        )

    return Ok(tuple(cleaned_pages))
