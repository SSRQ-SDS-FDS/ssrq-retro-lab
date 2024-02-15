import html

import fitz_new  # type: ignore


def extract_pages(
    pdf: fitz_new.Document,
    pages: tuple[int, ...],
) -> tuple[str, ...]:
    """Extracts the text from a range of pages.

    Args:
        pdf: The PDF to extract the text from.
        pages: The pages to extract the text from.

    Returns:
        The extracted text. Is uses the extractHTML from PyMuPDF to extract the text.
        See https://pymupdf.readthedocs.io/en/latest/textpage.html#TextPage.extractHTML
    """
    return tuple(
        _unescape_extracted_text(pdf.load_page(page).get_textpage().extractHTML())
        for page in _calc_pdf_pages(pages)
    )


def _unescape_extracted_text(text: str) -> str:
    """Unescapes the extracted text.

    Args:
        text: The text to unescape.

    Returns:
        The unescaped text.
    """
    return html.unescape(text)


def _calc_pdf_pages(
    pages: tuple[int, ...],
) -> range:
    """Calculates the pages to extract.

    Args:
        pages: The pages to extract.

    Returns:
        The pages to extract as a range."""

    start_page = min(pages) - 1  # PDF pages are 0-indexed
    end_page = max(pages)

    return range(start_page, end_page)
