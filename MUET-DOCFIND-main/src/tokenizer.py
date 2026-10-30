"""Tokenizer: the ONE set of text-cleaning rules shared by every search method.

Rules (in this order):
1. Lowercase everything.
2. Apostrophes (' and the curly one) are deleted:  student's -> students
3. Every other character that is not a letter or digit acts like a space,
   so punctuation and hyphens split words:        mid-term -> mid, term
4. Digits are kept:                                 Week 8 -> week, 8
5. Words found in STOP_WORDS are dropped.
6. Repeats are KEPT by tokenize(); unique_tokens() removes them when needed.
"""

STOP_WORDS = (
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "me", "my", "of", "on", "or",
    "our", "the", "this", "that", "to", "was", "we", "were", "what", "when",
    "where", "which", "who", "will", "with", "you", "your",
)
# Deliberately NOT stop words: "must", "not", "no", "should", "may".
# In rules text they change the meaning ("must attend" vs "not attend").


def tokenize(text):
    """Turn text into a list of lowercase tokens (repeats are kept)."""
    if not isinstance(text, str):
        raise TypeError("tokenize() needs a string, but got " + type(text).__name__)

    lowered = text.lower()

    cleaned = ""
    for character in lowered:
        if character == "'" or character == "\u2019":
            continue  # delete apostrophes, do not split the word
        if character.isalnum():
            cleaned = cleaned + character
        else:
            cleaned = cleaned + " "

    tokens = []
    for word in cleaned.split():
        if word not in STOP_WORDS:
            tokens.append(word)
    return tokens


def unique_tokens(tokens):
    """Return the tokens with repeats removed, keeping the first-seen order."""
    result = []
    for token in tokens:
        if token not in result:
            result.append(token)
    return result


if __name__ == "__main__":
    examples = [
        "Data Structures",
        "Lab rules, (strict)!",
        "The mid-term exam is in Week 8.",
        "Students' attendance and student\u2019s ID card",
        "data data DATA",
        "the of and",
        "",
        "   ",
        "!!! ???",
    ]
    for example in examples:
        print(f"{example!r:45} -> {tokenize(example)}")