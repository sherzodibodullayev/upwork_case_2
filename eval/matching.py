"""Shared text matching for the eval set.

Used by both the question checker and the scorer. They must agree: if the checker
accepts a phrase as present in a document but the scorer would not accept the same
phrase in an answer, every score is quietly wrong.

Markdown wraps lines, so "**30\\ncalendar day**" contains the phrase "30 calendar
day" to a reader and not to a naive substring search. Normalising collapses
whitespace and drops emphasis markers before comparing.
"""
import re

_EMPHASIS = re.compile(r"[*_`]+")
# Table cell walls become a barrier, not blank space: stripping them outright turns
# "| S1 | 15 minutes |" into "s1 15 minutes" and lets a phrase match across two
# unrelated cells. A needle never contains this marker, so it can never match through.
_CELL = re.compile(r"\|+")
_SPACE = re.compile(r"\s+")
BARRIER = " ¦ "


def normalize(text):
    """Lowercase, drop markdown emphasis, collapse whitespace, wall off table cells."""
    t = _EMPHASIS.sub(" ", text.lower())
    t = _CELL.sub(BARRIER, t)
    return _SPACE.sub(" ", t).strip()


def group_hit(group, text):
    """True when any alternative in the group appears in already-normalised text."""
    return any(normalize(alt) in text for alt in group)


def missing_groups(groups, text):
    """Which OR-groups are absent. Empty list means every requirement is met."""
    norm = normalize(text)
    return [g for g in groups if not group_hit(g, norm)]


def demo():
    wrapped = "a formal request with a **30\ncalendar day** deadline"
    assert not missing_groups([["30 calendar day"]], wrapped), \
        "a phrase split across a line break must still count as present"
    assert missing_groups([["60 calendar day"]], wrapped)

    assert not missing_groups([["fifteen minute", "15 minute"]], "within 15 minutes")
    assert not missing_groups([["S1"]], "severity s1 applies")
    assert missing_groups([["45"], ["30"]], "the stipend is $45 per month") == [["30"]], \
        "each group is required independently"
    assert not missing_groups([], "anything"), "no requirements means nothing missing"

    # Table pipes must not glue cells together into false matches.
    assert missing_groups([["s1 15"]], "| S1 | 15 minutes |"), \
        "a phrase spanning two table cells must not count as present"
    assert not missing_groups([["15 minute"]], "| S1 | 15 minutes |"), \
        "but a phrase inside one cell still counts"
    print("demo ok")


if __name__ == "__main__":
    demo()
