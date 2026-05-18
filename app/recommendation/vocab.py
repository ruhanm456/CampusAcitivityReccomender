TAG_VOCAB = [
    "academic_stem_tech",
    "business_career",
    "creative_arts",
    "sports",
    "gaming",
    "service",
    "activism_environment",
    "politics",
    "cultural",
    "faith",
]

TAG_INDEX = {tag: idx for idx, tag in enumerate(TAG_VOCAB)}


def get_tag_index(tag: str) -> int:
    """Return the index for a tag, raising KeyError if the tag is not in the vocabulary."""
    return TAG_INDEX[tag]


def is_valid_tag(tag: str) -> bool:
    """Return True when the tag exists in the shared vocabulary."""
    return tag in TAG_INDEX
