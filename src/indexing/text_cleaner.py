import re
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize extracted knowledge-source text.

    Goals:
    - Preserve legitimate Unicode characters.
    - Normalize Unicode representation.
    - Normalize line endings.
    - Remove problematic control characters.
    - Remove trailing whitespace.
    - Collapse excessive blank lines.

    This function must not perform ASCII conversion.
    """

    if not text:
        return ""

    # ---------------------------------------------------------
    # 1. Unicode normalization
    # ---------------------------------------------------------
    text = unicodedata.normalize("NFC", text)

    # ---------------------------------------------------------
    # 2. Normalize line endings
    # ---------------------------------------------------------
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # ---------------------------------------------------------
    # 3. Remove control characters
    #
    # Preserve:
    #   \n  newline
    #   \t  tab
    #
    # Remove other Unicode control/format characters that
    # can interfere with chunking and retrieval.
    # ---------------------------------------------------------
    cleaned_chars = []

    for char in text:
        category = unicodedata.category(char)

        if char in ("\n", "\t"):
            cleaned_chars.append(char)

        elif category.startswith("C"):
            continue

        else:
            cleaned_chars.append(char)

    text = "".join(cleaned_chars)

    # ---------------------------------------------------------
    # 4. Normalize spaces around lines
    # ---------------------------------------------------------
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            lines.append(line)
        else:
            # Preserve blank lines temporarily.
            lines.append("")

    text = "\n".join(lines)

    # ---------------------------------------------------------
    # 5. Collapse excessive blank lines
    #
    # Keep at most one blank line between content blocks.
    # ---------------------------------------------------------
    text = re.sub(r"\n{3,}", "\n\n", text)

    # ---------------------------------------------------------
    # 6. Final cleanup
    # ---------------------------------------------------------
    return text.strip()