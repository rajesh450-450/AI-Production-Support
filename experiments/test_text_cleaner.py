from src.indexing.text_cleaner import normalize_text


def main():

    test_text = """
    Production Support

    Observe → Identify → Investigate → Act → Validate

    Architecture — Production Data Platform

    Line with     multiple spaces.

    """

    cleaned = normalize_text(test_text)

    print("=" * 80)
    print("TEXT NORMALIZATION TEST")
    print("=" * 80)

    print("\nOriginal:")
    print(repr(test_text))

    print("\nNormalized:")
    print(repr(cleaned))

    print("\nNormalized text:")
    print(cleaned)

    print("\nValidation:")

    assert "→" in cleaned
    assert "—" in cleaned

    assert "\r" not in cleaned

    assert "\n\n\n" not in cleaned

    assert cleaned

    print("PASS: Unicode characters preserved")
    print("PASS: Line endings normalized")
    print("PASS: Excessive blank lines removed")
    print("PASS: Text normalization successful")


if __name__ == "__main__":
    main()