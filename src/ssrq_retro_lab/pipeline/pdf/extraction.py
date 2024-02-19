import html

import fitz  # type: ignore

from ssrq_retro_lab.pipeline.parser.xml_toc_parser import XMLToC, VolumeEntry


def extract_pages(
    pdf: fitz.Document, toc: XMLToC, entry: VolumeEntry
) -> tuple[str, ...]:
    """Extracts the text from a range of pages.

    Args:
        pdf: The PDF to extract the text from.
        pages: The pages to extract the text from.

    Returns:
        The extracted text. Is uses the extractHTML from PyMuPDF to extract the text.
        See https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractHTML
    """
    print(entry)
    return tuple(
        _unescape_extracted_text(pdf.load_page(page).get_textpage().extractHTML())
        for page in _calc_pdf_pages(toc, entry)
    )


def _unescape_extracted_text(text: str) -> str:
    """Unescapes the extracted text.

    Args:
        text: The text to unescape.

    Returns:
        The unescaped text.
    """
    return html.unescape(text)


def _calc_pdf_pages(toc: XMLToC, entry: VolumeEntry) -> range:
    """Calculates the pages to extract.

    Args:
        pages: The pages to extract.

    Returns:
        The pages to extract as a range."""

    start_page = toc.page_to_image[min(entry.pages)]
    end_page = toc.page_to_image[max(entry.pages)]

    return range(start_page - 1, end_page)
