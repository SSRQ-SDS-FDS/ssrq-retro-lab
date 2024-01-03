def split_content(content: str, strip_lines: bool = True) -> list[str]:
    """Splits the contents of a text file
    into a list of different 'documents' based on
    empty lines separating them.

    Args:
        content: The contents of the file.
        strip_lines: Whether to strip the lines of the documents.

    Returns:
        A list of documents.
    """
    return [
        "\n".join(
            line.strip() if strip_lines else line
            for line in document.strip().splitlines()
        )
        for document in content.split("\n\n")
    ]
