import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Writer(ABC):
    """Write a file to a given path.

    Attributes:
        path: The path to the file to read.
    """

    path: Path

    def __init__(self, path: Path):
        """Initializes a new Writer instance.

        Args:
            path: The path where the file should be written to.
        """
        self.path = path

    @abstractmethod
    def write(self, content: Any) -> None:
        """Writes the file

        Returns:
            None.
        """
        ...


class JSONLWriter(Writer):
    """Writes a JSONL file to a given path.

    Attributes:
        path: The path where the file should be written to.
    """

    def write(self, content: list[dict]):
        """Writes a JSONL file.

        Args:
            content: The content to write to the file.

        Returns:
            None.
        """
        with open(self.path, "w") as jsonl_file:
            for item in content:
                jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")
