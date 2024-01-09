import json
from abc import ABC, abstractmethod
from pathlib import Path

import fitz_new  # type: ignore


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
    def read(self) -> str:
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
        with open(self.path, "rb") as binary_file:
            return binary_file