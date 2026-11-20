#!/usr/bin/env python3
"""Prints chapter 11's table of sentences, rendered from v31/sentences.json.

Usage: render-sentences.py [sentences.json]. The chapter cell is the document's chapter number
and the title of the heading of that chapter under which the sentence is given ("1 · Refusals"). The
title is the design's section title (number dropped), except for the rows in HEADING_OF, whose
design section is not a heading of the document. The sentence cell is *"..."* with these written
as escapes: <, >, | and *, and a backslash before punctuation. A quotation mark is not escaped
(parse() takes the cell between its first two and last two characters, so it round-trips).
"""
import json
import re
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "v31" / "sentences.json"
HEADER = ["| Id | Chapter | Sentence | Audience |", "|---|---|---|---|"]
# The design's part number to the document's chapter: the record (part 08) is chapter 9
# and the engine and pages (part 09) are chapter 8; every other part keeps its number.
CHAPTER_OF_PART = {"01": 1, "02": 2, "03": 3, "04": 4, "05": 5, "06": 6, "07": 7,
                   "08": 9, "09": 8, "10": 10}
# Sentence id to the heading of the document where the sentence is given, for the rows whose
# design section (in sentences.json, which stays the design's text) is not a heading of the chapter.
HEADING_OF = {
    "S02-005": "Refusals",
    "S08-001": "Sentences the record holds", "S08-002": "Sentences the record holds",
    "S08-003": "Sentences the record holds", "S08-004": "Sentences the record holds",
    "S08-005": "Sentences the record holds", "S08-006": "Sentences the record holds",
    "S08-007": "Sentences the record holds", "S08-008": "Sentences the record holds",
    "S08-009": "Sentences the record holds",
    "S09-004": "Sentences the pages show", "S09-005": "Sentences the pages show",
    "S09-006": "Sentences the pages show", "S09-007": "Sentences the pages show",
    "S09-008": "Sentences the engine shows", "S09-009": "Sentences the engine shows",
    "S09-010": "Sentences the engine shows", "S09-011": "Sentences the engine shows",
    "S09-012": "Sentences the engine shows", "S09-013": "Sentences the engine shows",
    "S09-014": "Sentences the engine shows", "S09-015": "Sentences the engine shows",
    "S10-003": "What the converter refuses, and `!x` on text",
    "S10-004": "Hand edits, with notices",
    "S10-005": "A package that stays at 30, and what its owner is told",
    "S10-006": "Reserved ids are renamed",
}
SECTION_NUMBER = re.compile(r"^\d+(\.\d+)*\.?\s+")
ESCAPED = re.compile(r"[<>|*]|\\(?=[!-/:-@\[-`{-~])")
UNESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def escape(text):
    return ESCAPED.sub(lambda match: "\\" + match.group(0), text)


def chapter_cell(sentence):
    """The chapter number and the heading's title, as "1 · Refusals" (the section number dropped)."""
    title = HEADING_OF.get(sentence["id"]) or SECTION_NUMBER.sub("", sentence["section"])
    return f"{CHAPTER_OF_PART[sentence['part']]} · {escape(title)}"


def render(sentences):
    rows = [f"| {s['id']} | {chapter_cell(s)} | *\"{escape(s['sentence'])}\"* | {s['audience']} |"
            for s in sentences]
    return "\n".join(HEADER + rows) + "\n"


def parse(table):
    """Returns (id, sentence, audience) for each row of a table render() wrote."""
    rows = []
    for line in table.splitlines()[len(HEADER):]:
        id_, _chapter, cell, audience = [c.strip() for c in CELL_SPLIT.split(line)[1:-1]]
        rows.append((id_, UNESCAPE.sub(r"\1", cell[2:-2]), audience))
    return rows


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    sys.stdout.write(render(json.loads(path.read_text(encoding="utf-8"))["sentences"]))


if __name__ == "__main__":
    main()
