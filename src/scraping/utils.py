from transliterate import translit


def from_cyrillic_to_eng(ru_text: str):
    text = translit(ru_text, language_code='ru', reversed=True).replace(' ', '_')
    return text


