from dataclasses import dataclass
from pathlib import Path

from parsel import Selector
from result import Err, Ok, Result, is_err, is_ok


class XMLToCParsingError(Exception):
    """Base class for XMLToC parsing errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass(slots=True, frozen=True)
class VolumeEntry:
    title: str
    date: str
    no: int
    pages: tuple[int, ...]


@dataclass(slots=True, frozen=True)
class VolumeMeta:
    canton: str
    title: str
    volume: str


@dataclass(frozen=True, slots=True)
class XMLToC:
    entries: tuple[VolumeEntry, ...]
    meta: VolumeMeta
    volume_path: Path
    page_to_image: dict[int, int]

    def get_entry(self, article_number: int) -> Result[VolumeEntry, XMLToCParsingError]:
        """Gets the volume entry for a given article number.

        Args:
            article_number: The article number.

        Returns:
            The volume entry as Result with VolumeEntry as Ok value
            or an XMLToCParsingError as Err value.
        """
        entry = next(
            (entry for entry in self.entries if entry.no == article_number), None
        )

        return (
            Ok(entry)
            if entry
            else Err(
                XMLToCParsingError(
                    f"Found no entry for article number >>{article_number}<< in {self.meta.canton} {self.meta.volume} with title {self.meta.title}"
                )
            )
        )


def parse_xml_toc(
    toc: Selector, volume_path: Path
) -> Result[XMLToC, XMLToCParsingError]:
    """Parses the XML table of contents, which
    describes the structure of a (printed) volume.

    Args:
        toc: The table of contents as a Selector.
        volume_path: The path to the volume.

    Returns:
        The parsed table of contents as Result with XMLToC as Ok value
        or an XMLToCParsingError as Err value."""
    meta = _get_volume_meta_infos(toc)

    if is_err(meta):
        return meta

    entries = _get_volume_entries(toc)

    if is_err(entries):
        return entries

    pages_to_img = _map_book_pages_to_img(toc)

    if is_err(pages_to_img):
        return pages_to_img

    return Ok(
        XMLToC(entries.unwrap(), meta.unwrap(), volume_path, pages_to_img.unwrap())
    )


def _get_volume_meta_infos(toc: Selector) -> Result[VolumeMeta, XMLToCParsingError]:
    canton = toc.xpath("/volinfo/@canton").get()
    title = toc.xpath("/volinfo/title/text()").get()
    volume = toc.xpath("/volinfo/@vol").get()

    return (
        Ok(VolumeMeta(canton, title, volume))
        if canton and title and volume
        else Err(
            XMLToCParsingError(
                f"Found invalid volume meta infos: {canton}, {title}, {volume}"
            )
        )
    )


def _get_volume_entries(
    toc: Selector,
) -> Result[tuple[VolumeEntry, ...], XMLToCParsingError]:
    """Retrieves the volume entries from the table of contents.

    Args:
        toc: The table of contents.

    Returns:
        The volume entries as Result with tuple of VolumeEntry as Ok value
        or an XMLToCParsingError as Err value.
    """
    entries = toc.xpath("//entry[date][not(entry[date])]")

    parsed_entries = tuple(_parse_entry(entry, toc) for entry in entries)
    return (
        Ok(tuple(e.unwrap() for e in parsed_entries))
        if all(is_ok(e) for e in parsed_entries)
        else Err(
            XMLToCParsingError(
                "Found invalid volume entries: "
                + ", ".join(e.unwrap_err().message for e in parsed_entries if is_err(e))
            )
        )
    )


def _parse_entry(
    entry: Selector, toc: Selector
) -> Result[VolumeEntry, XMLToCParsingError]:
    """Parses a single volume entry.

    Args:
        entry: The entry to parse.
        toc: The table of contents.

    Returns:
        The parsed volume entry as Result with VolumeEntry as Ok value
        or an XMLToCParsingError as Err value.
    """
    title = entry.xpath("title/text()").get()
    date = entry.xpath("date/text()").get()
    no = entry.xpath("no/text()").get()

    if no is None:
        return Err(
            XMLToCParsingError(
                f"Found invalid volume entry with title {title}: No number"
            )
        )

    article_number = int(no)

    start_page = int(pg) if (pg := entry.xpath("pg/text()").get()) else None

    if start_page is None:
        return Err(
            XMLToCParsingError(
                f"Found invalid volume entry with number {article_number}: No start page"
            )
        )

    pages = _get_pages(toc, article_number, start_page)

    if is_err(pages):
        return pages

    return (
        Ok(VolumeEntry(title, date, int(no), pages.unwrap()))
        if title and date and no and pages
        else Err(
            XMLToCParsingError(
                f"Found invalid volume entry: {title}, {date}, {no}, {pages}"
            )
        )
    )


def _get_pages(
    toc: Selector, article_number: int, start_page: int
) -> Result[tuple[int, ...], XMLToCParsingError]:
    """Gets the pages for a given article number.

    Args:
        toc: The table of contents.
        article_number: The article number.
        start_page: The start page.

    Returns:
        The pages as Result with tuple of int as Ok value
        or an XMLToCParsingError as Err value."""
    try:
        end_pages = toc.xpath(
            f"//entry[date][not(entry[date])][no/text() = '{article_number + 1!s}']/pg/text()"
        ).getall()

        end_page = sorted(
            [page for p in end_pages if p and (page := int(p)) >= start_page]
        )

        """ToDo: Find a better way to get the end page. This is a workaround."""
        article_end_page = end_page[0] if len(end_page) > 0 else start_page

        pages = (
            tuple(
                range(
                    start_page,
                    article_end_page + 1,
                )
            )
            if article_end_page >= start_page
            else (start_page,)
        )

        return Ok(pages)
    except Exception as e:
        return Err(
            XMLToCParsingError(f"Error while getting pages for {article_number}: {e}")
        )


def _map_book_pages_to_img(toc: Selector) -> Result[dict[int, int], XMLToCParsingError]:
    """Maps the book pages to the image pages.

    Args:
        toc: The table of contents.

    Returns:
        The mapping as dict with int as key and int as value."""
    pages_to_image: dict[int, int] = {}
    page_ranges = toc.xpath("//pages/range[@type = 'number']")

    if len(page_ranges) == 0:
        return Err(XMLToCParsingError("Found no page ranges"))

    for page_range in page_ranges:
        page_from = int(page_range.xpath("@from").get())  # type: ignore
        page_to = int(page_range.xpath("@to").get())  # type: ignore
        page_start = int(page_range.xpath("@start").get())  # type: ignore

        for page in range(page_from - 1, page_to):
            pages_to_image[page_start] = page + 1
            page_start += 1

    return Ok(pages_to_image)
