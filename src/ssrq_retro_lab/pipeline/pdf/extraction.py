import html

import fitz_new  # type: ignore


def extract_pages(
    pdf: fitz_new.Document,
    pages: tuple[int, ...],
    skip_pages: int = 0,
    real_start: int = 0,
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
        for page in _calc_pdf_pages(pages, skip_pages, real_start)
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
    pages: tuple[int, ...], skip_pages: int = 0, real_start: int = 0
) -> range:
    """Calculates the pages to extract.

    Args:
        pages: The pages to extract.
        skip_pages: The number of pages to skip.
        real_start: The real start page.

    Returns:
        The pages to extract as a range."""

    start_page = skip_pages + min(pages) - real_start - 1  # PDF pages are 0-indexed
    end_page = skip_pages + max(pages) - real_start

    return range(start_page, end_page)
