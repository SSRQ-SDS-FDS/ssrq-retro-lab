import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import fitz_new  # type: ignore
from parsel import Selector


class Reader(ABC):
    """Reads a file from a given path.

    Attributes:
        path: The path to the file to read.
    """

    path: Path

    def __init__(self, path: Path):
        """Initializes a new Reader instance.

        Args:
            path: The path to the file to read.
        """
        self.path = path

    @abstractmethod
    def read(self) -> Any:
        """Reads the file.

        Returns:
            The file contents.
        """
        ...


class TextReader(Reader):
    """Reads a text file from a given path.

    Attributes:
        path: The path to the file to read.
    """

    def read(self) -> str:
        """Reads a simple text file.

        Returns:
            The file contents.
        """
        with open(self.path, encoding="utf-8") as file:
            return file.read()


class PDFReader(Reader):
    def read(self) -> fitz_new.Document:
        """Reads a PDF file.

        Returns:
            The file as a fitz Document.
        """
        return fitz_new.open(self.path)


class JSONLReader(Reader):
    def read(self):
        """Reads a JSONL file.

        Returns:
            The content of the JSONL file.
        """
        with open(self.path, encoding="utf-8") as jsonl_file:
            return [json.loads(line) for line in jsonl_file]


class BufferBinaryReader(Reader):
    def read(self):
        return open(self.path, "rb")


class XMLReader(Reader):
    """Reads an XML file from a given path.

    Attributes:
        path: The path to the file to read.

    Returns:
        The file contents, when read is called."""

    def read(self) -> Selector:
        return Selector(TextReader(self.path).read(), type="xml")
