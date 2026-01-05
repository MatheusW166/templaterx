from faker import Faker

faker_pt_BR = Faker(locale="pt_BR")


def fake_word_list(size: int = 5) -> list[str]:
    """
    Generates a list of fake words with a fixed size.

    Args:
        size: Number of elements to generate (default: 5)

    Returns:
        A list of fake words.
    """
    return [faker_pt_BR.word() for _ in range(size)]
