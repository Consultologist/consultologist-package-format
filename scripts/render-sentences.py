#!/usr/bin/env python3
"""Prints chapter 11's table of sentences, rendered from v31/sentences.json.

Usage: render-sentences.py [sentences.json]. The chapter cell is the document's chapter number
and the section's title ("1 · Refusals"). The sentence cell is *"..."* with these written
as escapes: <, >, | and *, and a backslash before punctuation.
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
SECTION_NUMBER = re.compile(r"^\d+(\.\d+)*\.?\s+")
ESCAPED = re.compile(r"[<>|*]|\\(?=[!-/:-@\[-`{-~])")
UNESCAPE = re.compile(r"\\([!-/:-@\[-`{-~])")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def escape(text):
    return ESCAPED.sub(lambda match: "\\" + match.group(0), text)


def chapter_cell(sentence):
    """The chapter number and the section's title, as "1 · Refusals" (the design's section number dropped)."""
    title = SECTION_NUMBER.sub("", sentence["section"])
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
