from enum import Enum


# just an enum https://en.wikipedia.org/wiki/Enumerated_type
class SearchMode(Enum):
    EXACT = "sprv",
    NON_STRICT = "typd",
