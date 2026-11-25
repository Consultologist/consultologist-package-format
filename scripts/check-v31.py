#!/usr/bin/env python3
"""Checks the specVersion 31 preview files. Exits 0 when every group passes, 1 otherwise.

Each group is a function check_<group>() -> list[str] of failures, registered in CHECKS.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
V31 = ROOT / "v31"

# Part 01 section 7, "bounds.json's shape", exactly.
BOUNDS = {
    "specVersion": 31,
    "sourceBounds": {"files": 512, "fileBytes": 262144, "totalBytes": 2097152,
                     "pathLength": 200, "idLength": 64, "jsonDepth": 32,
                     "expressionNodes": 1000},
    "formatBounds": {"passes": 15, "depth": 15, "parallel": 15},
    "windowsReservedIds": ["con", "prn", "aux", "nul",
                           "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
                           "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"],
    "reservedIds": ["input", "inputs", "node", "nodes", "check", "checks", "function", "functions",
                    "test", "tests", "snippet", "snippets", "macro", "macros", "part", "parts",
                    "renderer", "renderers", "format", "formats", "deliverable", "deliverables",
                    "param", "params", "item", "items", "pass", "passes", "run", "runs",
                    "profile", "profiles", "value", "values", "content", "contents"],
}

# Part 07 section 3.1: the built-in custom operations.
OPERATIONS = ["size", "blank", "words", "lines", "lower", "trim", "starts_with", "ends_with",
              "plain", "object", "matches", "has_word", "terms_subset", "all_pass", "count_pass",
              "days_between", "years_between", "add_days"]

# Part 05 section 2.2: the template built-ins.
TEMPLATE_BUILTINS = ["string.upcase", "string.downcase", "string.capitalize", "string.strip",
                     "array.join", "array.size", "date.to_string"]

CONSTANTS_KEYS = ["specVersion", "dialects", "evaluator", "operations", "builtins",
                  "templateBuiltins", "standardOperations", "kinds", "features", "producers",
                  "runFacts", "channels", "deliveryKinds", "whenEmpty", "states",
                  "deliverableStates", "edgeKinds", "limits", "mediaTypes", "markdig"]
LIMITS_KEYS = ["descriptionCodePoints", "matchesPatternCodePoints", "matchesRepetition",
               "matchesTextBytes", "templateForIterations", "templateNesting",
               "templateOutputBytes", "testsSeconds", "itemNameCharacters"]
BUILTINS_KEYS = ["concept_bullets", "concept_context", "formats", "markdown_escape",
                 "plain_conversion", "printer"]

# Constants' list and object members, value for value (parts 01 to 09).
CONSTANT_MEMBERS = {
    "standardOperations": ["var", "missing", "if", "===", "!==", "<", "<=", ">", ">=", "and", "or",
                           "!", "in", "cat", "+", "-", "*", "/", "%", "min", "max"],
    "kinds": ["agent", "rendered", "computed", "for", "while", "if", "case", "call"],
    "features": ["parallel", "macro-markers", "parts", "run-spots", "check-loops"],
    "producers": {"accepted": ["generated", "computed"],
                  "reserved": ["grounded", "extracted", "attention"]},
    "runFacts": ["date", "id", "package", "engine"],
    "channels": ["transcript", "image", "ambient-note", "form"],
    "deliveryKinds": ["email", "pdf", "emr", "zip"],
    "whenEmpty": ["release", "hold", "fail"],
    "states": ["completed", "skipped", "not_run"],
    "deliverableStates": ["released", "held", "failed", "skipped", "blocked"],
    "edgeKinds": ["reads", "if", "for", "ret", "placed", "calls", "aligned", "gates"],
    "mediaTypes": {"resolve": "application/vnd.consultologist.resolve+json",
                   "lock": "application/vnd.consultologist.lock+json",
                   "publishReport": "application/vnd.consultologist.publish-report+json"},
    "limits": {"descriptionCodePoints": 500, "matchesPatternCodePoints": 200,
               "matchesRepetition": 100, "matchesTextBytes": 1048576,
               "templateForIterations": 1000, "templateNesting": 15,
               "templateOutputBytes": 1048576, "testsSeconds": 60, "itemNameCharacters": 120},
}

PROFILE_FIELDS = {  # field -> (format, label), part 06 section 10.1 and part 09 section 9
    "name": ("string", "name"),
    "credentials": ("string", "credentials"),
    "organisation": ("string", "organisation"),
    "signature": ("plaintext", "signature"),
    "closing": ("plaintext", "closing line"),
}


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"{path.relative_to(ROOT)}: missing"]
    except json.JSONDecodeError as error:
        return None, [f"{path.relative_to(ROOT)}: not JSON ({error})"]


def expect(failures, what, actual, expected):
    if actual != expected:
        failures.append(f"{what}: expected {expected!r}, found {actual!r}")


def check_constants():
    failures = []

    bounds, errors = load(V31 / "bounds.json")
    failures += errors
    if bounds is not None:
        expect(failures, "v31/bounds.json", bounds, BOUNDS)

    constants, errors = load(V31 / "constants.json")
    failures += errors
    if constants is not None:
        expect(failures, "v31/constants.json keys", list(constants), CONSTANTS_KEYS)
        expect(failures, "constants.specVersion", constants.get("specVersion"), 31)
        expect(failures, "constants.operations", constants.get("operations"),
               {name: "1.0.0" for name in OPERATIONS})
        expect(failures, "constants.templateBuiltins", constants.get("templateBuiltins"),
               {name: "1.0.0" for name in TEMPLATE_BUILTINS})
        expect(failures, "constants.builtins", constants.get("builtins"),
               {name: "1.0.0" for name in BUILTINS_KEYS})
        expect(failures, "constants.evaluator", constants.get("evaluator"), "1.0.0")
        expect(failures, "constants.limits keys", list(constants.get("limits", {})), LIMITS_KEYS)
        for name, expected in CONSTANT_MEMBERS.items():
            expect(failures, f"constants.{name}", constants.get(name), expected)
        markdig = constants.get("markdig", {})
        expect(failures, "constants.markdig keys", list(markdig), ["version", "extensions"])
        if not re.fullmatch(r"0\.41\.\d+", str(markdig.get("version"))):
            failures.append(f"constants.markdig.version: expected 0.41.x, found {markdig.get('version')!r}")
        if not markdig.get("extensions"):
            failures.append("constants.markdig.extensions: empty")

    profile, errors = load(V31 / "profile.json")
    failures += errors
    if profile is not None:
        expect(failures, "v31/profile.json keys", list(profile),
               ["specVersion", "fields", "previewTimeZone"])
        expect(failures, "profile.previewTimeZone", profile.get("previewTimeZone"),
               "America/Toronto")
        fields = profile.get("fields", {})
        expect(failures, "profile.fields", list(fields), list(PROFILE_FIELDS))
        for name, (fmt, label) in PROFILE_FIELDS.items():
            field = fields.get(name, {})
            expect(failures, f"profile.fields.{name} keys", list(field),
                   ["format", "label", "preview"])
            expect(failures, f"profile.fields.{name}.format", field.get("format"), fmt)
            expect(failures, f"profile.fields.{name}.label", field.get("label"), label)
            preview = field.get("preview")
            if not isinstance(preview, str) or not preview:
                failures.append(f"profile.fields.{name}.preview: expected a non-empty string, found {preview!r}")

    versions, errors = load(ROOT / "spec-versions.json")
    failures += errors
    if versions is not None:
        expect(failures, "spec-versions.json preview", versions.get("preview", {}).get("31"),
               {"document": "package-format-v31.md", "directory": "v31"})
        if 31 in versions.get("supported", []):
            failures.append("spec-versions.json: 31 is in supported")
        if "31" in versions.get("documents", {}):
            failures.append("spec-versions.json: 31 is in documents")
    return failures


# Rows of each part of the design's refusal-sentences.md (the table, not its totals).
SENTENCE_COUNTS = {"01": 42, "02": 56, "03": 44, "04": 80, "05": 64,
                   "06": 38, "07": 17, "08": 9, "09": 19, "10": 6}
SENTENCE_ID = re.compile(r"^S(0[1-9]|10)-\d{3}$")


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_sentences",
                                                  ROOT / "scripts" / "render-sentences.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sentences():
    document, failures = load(V31 / "sentences.json")
    if document is None:
        return failures
    expect(failures, "sentences.json keys", list(document), ["specVersion", "sentences"])
    expect(failures, "sentences.specVersion", document.get("specVersion"), 31)
    sentences = document.get("sentences", [])
    seen = set()
    last_in_part = {}
    counts = {}
    for entry in sentences:
        id_ = entry.get("id", "")
        expect(failures, f"{id_} keys", list(entry),
               ["id", "part", "section", "sentence", "audience"])
        if not SENTENCE_ID.match(id_):
            failures.append(f"{id_!r}: not an id of the form S<part>-<number>")
            continue
        if id_ in seen:
            failures.append(f"{id_}: duplicate id")
        seen.add(id_)
        part = id_[1:3]
        expect(failures, f"{id_}.part", entry.get("part"), part)
        if id_ <= last_in_part.get(part, ""):
            failures.append(f"{id_}: not ascending within part {part}")
        last_in_part[part] = id_
        counts[part] = counts.get(part, 0) + 1
        if entry.get("audience") not in ("author", "clinician"):
            failures.append(f"{id_}.audience: {entry.get('audience')!r}")
        text = entry.get("sentence")
        if not isinstance(text, str) or not text:
            failures.append(f"{id_}.sentence: expected a non-empty string")
            continue
        if re.search(r"\\[<>|]", text):
            failures.append(f"{id_}.sentence: a backslash before <, > or |")
        if not entry.get("section"):
            failures.append(f"{id_}.section: empty")
    expect(failures, "sentences per part", dict(sorted(counts.items())), SENTENCE_COUNTS)

    renderer = load_renderer()
    parsed = renderer.parse(renderer.render(sentences))
    expect(failures, "sentences rendered and parsed back",
           parsed, [(e["id"], e["sentence"], e["audience"]) for e in sentences])
    return failures

DIALECT_ID = "urn:consultologist:spec:31:dialect"
BUILT_IN_FORMATS = ["string", "number", "boolean", "date", "plaintext", "markdown_block",
                    "markdown_inline", "check_result", "judgement"]
# Part 02 section 5: the annotations each built-in carries at its root.
ANNOTATIONS = {"plaintext": ("text/plain", None),
               "markdown_block": ("text/markdown", "block"),
               "markdown_inline": ("text/markdown", "inline")}
SCHEMAS = V31 / "schemas"
CONFORMANCE = V31 / "conformance" / "schemas"


def schema_files():
    """The dialect and every file-kind schema. Built-in formats are data, never loaded here."""
    return [V31 / "dialect.schema.json"] + sorted(SCHEMAS.glob("*.schema.json"))


def build_registry():
    registry, failures = Registry(), []
    for path in schema_files():
        document, errors = load(path)
        failures += errors
        if document is not None:
            registry = registry.with_resource(document.get("$id", path.name),
                                              Resource.from_contents(document))
    return registry, failures


def schema_for(name):
    return V31 / "dialect.schema.json" if name == "dialect" else SCHEMAS / f"{name}.schema.json"


def validator_for(path, registry, failures):
    schema, errors = load(path)
    failures += errors
    if schema is None:
        return None
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:
        failures.append(f"{path.relative_to(ROOT)}: not a 2020-12 schema ({error.message})")
        return None
    return Draft202012Validator(schema, registry=registry)


def check_examples():
    registry, failures = build_registry()
    folders = sorted(path for path in CONFORMANCE.glob("*") if path.is_dir())
    if not folders:
        failures.append("v31/conformance/schemas: no schema directories")
    for folder in folders:
        valid = sorted(folder.glob("valid-*.json"))
        invalid = sorted(folder.glob("invalid-*.json"))
        if not valid:
            failures.append(f"{folder.relative_to(ROOT)}: no valid example")
        if not invalid:
            failures.append(f"{folder.relative_to(ROOT)}: no invalid example")
        validator = validator_for(schema_for(folder.name), registry, failures)
        if validator is None:
            continue
        schema_id = validator.schema["$id"]
        for path, expected in [(p, True) for p in valid] + [(p, False) for p in invalid]:
            example, errors = load(path)
            failures += errors
            if example is None:
                continue
            name = path.relative_to(ROOT)
            if list(example) not in (["about", "instance"], ["about", "against", "instance"]) \
                    or not example["about"]:
                failures.append(f"{name}: expected {{ about, [against,] instance }} with a non-empty about")
                continue
            judge = validator
            if "against" in example:
                judge = Draft202012Validator({"$ref": schema_id + example["against"]}, registry=registry)
            accepted = judge.is_valid(example["instance"])
            if accepted != expected:
                failures.append(f"{name}: expected the schema to "
                                f"{'accept' if expected else 'refuse'} it")
    return failures


def declared_but_not_required(schema, where):
    """Part 02 section 3.3, which a meta-schema cannot state: required lists every property."""
    failures = []
    if isinstance(schema, dict):
        properties = schema.get("properties")
        if isinstance(properties, dict) and sorted(schema.get("required", [])) != sorted(properties):
            failures.append(f"{where}: required must list exactly the declared properties")
        for key, value in schema.items():
            if key in ("properties", "$defs") and isinstance(value, dict):
                for name, child in value.items():
                    failures += declared_but_not_required(child, f"{where}/{key}/{name}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    failures += declared_but_not_required(child, f"{where}/{key}/{index}")
            elif isinstance(value, dict):
                failures += declared_but_not_required(value, f"{where}/{key}")
    return failures


def check_common(registry, constants, bounds):
    failures = []
    common, errors = load(SCHEMAS / "common.schema.json")
    failures += errors
    if common is None:
        return failures
    definitions = common.get("$defs", {})
    expect(failures, "common.schema.json $id", common.get("$id"),
           "urn:consultologist:spec:31:schema:common")
    expect(failures, "common.schema.json $defs", list(definitions),
           ["id", "label", "description", "formatRef", "textFormat", "sha256", "rootedKey",
            "jsonLogic", "condition", "referenceString"])
    operation = definitions.get("jsonLogic", {}).get("$defs", {}).get("operationName", {})
    expect(failures, "common jsonLogic operation names", operation.get("enum"),
           constants["standardOperations"] + list(constants["operations"]))
    expect(failures, "common id not-enum", definitions.get("id", {}).get("not", {}).get("enum"),
           bounds["reservedIds"] + bounds["windowsReservedIds"])

    def accepts(name, value):
        schema = {"$ref": f"urn:consultologist:spec:31:schema:common#/$defs/{name}"}
        return Draft202012Validator(schema, registry=registry).is_valid(value)

    cases = [
        ("id", "hpi_section", True), ("id", "Hpi", False), ("id", "node", False),
        ("id", "con", False), ("id", "a" * 65, False), ("id", "a" * 64, True),
        ("label", "Planning", True), ("label", "  ", False),
        ("description", None, True), ("description", ["a"], True), ("description", [], False),
        ("description", "a", False),
        ("formatRef", "plaintext", True), ("formatRef", {"type": "string"}, True),
        ("formatRef", {"$schema": DIALECT_ID, "type": "string"}, False),
        ("textFormat", "markdown_inline", True), ("textFormat", "string", False),
        ("sha256", "sha256:" + "0" * 64, True), ("sha256", "sha256:" + "G" * 64, False),
        ("rootedKey", "node.draft", True), ("rootedKey", "check.a.b", True),
        ("rootedKey", "draft", False), ("rootedKey", "run.date", False),
        ("jsonLogic", {"var": "input.kind.value"}, True), ("jsonLogic", {"var": ["a"]}, False),
        ("jsonLogic", {"!": [True]}, True), ("jsonLogic", {"!": True}, False),
        ("jsonLogic", {"object": {"a": 1}}, True), ("jsonLogic", {"object": [1]}, False),
        ("jsonLogic", {"eval": [1]}, False), ("jsonLogic", {"+": [1], "-": [1]}, False),
        ("jsonLogic", [1, {"size": [{"var": "node.a.value"}]}], True),
        ("jsonLogic", {"==": [1, 2]}, False),
        ("condition", None, True), ("condition", {"in": ["a", {"var": "node.a.value"}]}, True),
        ("referenceString", "item.value.title", True), ("referenceString", "pass", True),
        ("referenceString", "param.x", True), ("referenceString", "other.x", False),
    ]
    for name, value, expected in cases:
        if accepts(name, value) != expected:
            failures.append(f"common {name}: expected {value!r} to be "
                            f"{'accepted' if expected else 'refused'}")
    return failures


def check_formats():
    registry, failures = build_registry()
    constants, errors = load(V31 / "constants.json")
    failures += errors
    bounds, errors = load(V31 / "bounds.json")
    failures += errors
    if constants is not None and bounds is not None:
        failures += check_common(registry, constants, bounds)

    folder = V31 / "formats"
    index, errors = load(folder / "index.json")
    failures += errors
    items = []
    if index is not None:
        expect(failures, "formats/index.json keys", list(index), ["description", "items"])
        items = index.get("items", [])
        expect(failures, "formats/index.json items", items, BUILT_IN_FORMATS)
        description = index.get("description")
        if description is not None and not (isinstance(description, list) and description
                                            and all(isinstance(line, str) for line in description)):
            failures.append("formats/index.json: description is null or a list of lines")
    files = sorted(path.stem for path in folder.glob("*.json") if path.name != "index.json")
    expect(failures, "formats/ files", files, sorted(items))

    validator = validator_for(V31 / "dialect.schema.json", registry, failures)
    for name in files:
        path = folder / f"{name}.json"
        document, errors = load(path)
        failures += errors
        if document is None:
            continue
        label = f"formats/{name}.json"
        if validator is not None:
            for error in validator.iter_errors(document):
                failures.append(f"{label}: outside the dialect at /{'/'.join(map(str, error.path))}: "
                                f"{error.message}")
        expect(failures, f"{label} $id", document.get("$id"),
               f"urn:consultologist:spec:31:format:{name}")
        expect(failures, f"{label} $schema", document.get("$schema"), DIALECT_ID)
        media, markdown = ANNOTATIONS.get(name, (None, None))
        expect(failures, f"{label} contentMediaType", document.get("contentMediaType"), media)
        expect(failures, f"{label} x-markdown", document.get("x-markdown"), markdown)
        if not isinstance(document.get("description"), str) or not document["description"]:
            failures.append(f"{label}: no description")
        if document.get("type") == "object":
            for key, child in document["properties"].items():
                if not child.get("description"):
                    failures.append(f"{label}: property {key} has no description")
        failures += declared_but_not_required(document, label)
    return failures


# The registry's own files, each required, and the schema each must satisfy.
SELF = [("bounds", V31 / "bounds.json"), ("constants", V31 / "constants.json"),
        ("profile", V31 / "profile.json"), ("sentences", V31 / "sentences.json"),
        ("conformance-index", V31 / "conformance" / "index.json")]


def check_self():
    registry, failures = build_registry()
    for name, path in SELF:
        document, errors = load(path)
        failures += errors
        validator = validator_for(schema_for(name), registry, failures)
        if document is None or validator is None:
            continue
        for error in validator.iter_errors(document):
            failures.append(f"{path.relative_to(ROOT)}: /{'/'.join(map(str, error.path))}: {error.message}")
    return failures


# The renderers chapter 5 section 5.5.1 prints whole, byte for byte.
PRINTED_RENDERERS = ["concept_bullets"]


def check_renderers():
    """Part 05 section 5.1: each renderer file is a header, then a non-empty body of its own."""
    registry, failures = build_registry()
    validator = validator_for(schema_for("renderer"), registry, failures)
    index, errors = load(V31 / "renderers" / "index.json")
    failures += errors
    listed = index["items"] if index else []
    for path in sorted((V31 / "renderers").glob("*.md")):
        where = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        parts = text.split("\n---\n", 1) if text.startswith("---\n") else None
        if parts is None:
            failures.append(f"{where}: does not start with a --- line")
            continue
        header_text, body = parts[0][4:], parts[1] if len(parts) > 1 else ""
        try:
            header = json.loads(header_text)
        except json.JSONDecodeError as error:
            failures.append(f"{where}: the header is not JSON ({error})")
            continue
        if validator:
            for error in validator.iter_errors(header):
                failures.append(f"{where}: header /{'/'.join(map(str, error.path))}: {error.message}")
        if path.stem not in listed:
            failures.append(f"{where}: not listed in renderers/index.json")
        if not body.strip():
            failures.append(f"{where}: the body is empty")
        if "renderer." in body:
            failures.append(f"{where}: the body pipes into a renderer")
    for item in listed:
        if not (V31 / "renderers" / f"{item}.md").exists():
            failures.append(f"renderers/index.json: {item} has no file")
    document = DOCUMENT.read_text(encoding="utf-8") if DOCUMENT.exists() else ""
    for item in PRINTED_RENDERERS:
        path = V31 / "renderers" / f"{item}.md"
        if path.exists() and f"```\n{path.read_text(encoding='utf-8')}```\n" not in document:
            failures.append(f"{DOCUMENT.name}: no code block prints {path.relative_to(ROOT)} as it is")
    return failures


DOCUMENT = ROOT / "package-format-v31.md"
DIALECT_DOCUMENT = V31 / "scriban-dialect.md"
DIALECT_VERSION = "scriban-dialect@1.0.0"
CHAPTERS_WRITTEN = 12
SENTENCES_CHAPTER = 11
CONFORMANCE_CHAPTER = 12
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


def github_slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped, spaces to hyphens."""
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")


def prose_lines(text):
    """The document's lines outside fenced code blocks, as (line number, line)."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def plain(text):
    """Text as a reader sees it: no emphasis markers, no backslash escapes, one space between words."""
    text = text.replace("*", "")
    text = re.sub(r"\\(.)", r"\1", text)
    return re.sub(r"\s+", " ", text)


def parses(text):
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def unescaped_tags(text, name):
    """GitHub drops an unknown <tag> from prose: a placeholder outside code is written \\<…\\>."""
    failures = []
    for number, line in prose_lines(text):
        if re.search(r"(?<!\\)<[A-Za-z]", re.sub(r"`[^`]*`", "", line)):
            failures.append(f"{name} line {number}: unescaped < before a letter: {line.strip()[:60]}")
    return failures


def chapter_bodies(text):
    """Each chapter's text, by number: the lines under its `## N.` heading, fenced code included."""
    bodies, current, fenced = {}, None, False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"## (\d+)\. ", line)
        if heading:
            current = int(heading.group(1))
            bodies[current] = ""
        elif current is not None:
            bodies[current] += line + "\n"
    return bodies


def heading_sections(text):
    """Every heading of the document as (chapter number, title without its number, text under it, subsections included)."""
    lines, found, fenced = text.splitlines(), [], False
    for number, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"(#{2,6}) (.*)", line)
        if heading:
            found.append((number, len(heading.group(1)), heading.group(2)))
    sections, chapter = [], 0
    for position, (number, level, title) in enumerate(found):
        end = next((n for n, deeper, _ in found[position + 1:] if deeper <= level), len(lines))
        if level == 2:
            chapter = int(title.split(".")[0]) if re.match(r"\d+\. ", title) else 0
        sections.append((chapter, re.sub(r"^[\d.]+\s+", "", title), "\n".join(lines[number + 1:end])))
    return sections


def check_chapter_cells(text, table):
    """Each row's Chapter cell names a heading of that chapter, and the row's sentence is given under it."""
    failures, sections = [], heading_sections(text)
    for line in table[2:]:
        id_, cell, sentence = [c.strip() for c in table_cells(line)[:3]]
        chapter, _, title = cell.partition(" · ")
        title = re.sub(r"\\(.)", r"\1", title)
        if not any(number == int(chapter) and name == title and plain(sentence) in plain(body)
                   for number, name, body in sections):
            failures.append(f"{id_}: no heading '{title}' in chapter {chapter} gives the sentence")
    return failures


def table_cells(row):
    """A table row's cells: the id, the Chapter cell, and the sentence without its *\"…\"* frame."""
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)[1:-1]]
    return [cells[0], cells[1], cells[2][2:-2]]


def check_document():
    if not DOCUMENT.exists():
        return [f"{DOCUMENT.name}: missing"]
    text = DOCUMENT.read_text(encoding="utf-8")
    failures = []
    if "specVersion 31" not in text:
        failures.append("the document never says 'specVersion 31'")
    chapters = [int(m.group(1)) for _, line in prose_lines(text)
                if (m := re.match(r"## (\d+)\. ", line))]
    if chapters != list(range(1, CHAPTERS_WRITTEN + 1)):
        failures.append(f"chapter headings are {chapters}, expected 1 to {CHAPTERS_WRITTEN} in order")
    slugs, seen = set(), {}
    for _, line in prose_lines(text):
        heading = re.match(r"#{1,6} (.*)", line)
        if heading:
            slug = github_slug(heading.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            slugs.add(slug if count == 0 else f"{slug}-{count}")
    for marker in ("/blob/main/", "/tree/main/"):
        if marker in text:
            failures.append(f"a link contains {marker}")
    for number, line in prose_lines(text):
        stripped = line.strip()
        if (re.match(r"[.,;:](\s|$)", stripped) or (stripped and not stripped.startswith("```")
                and not re.fullmatch(r"[-|: ]+|[-*+]|\d+\.", stripped)
                and re.fullmatch(r"[^\w{}\[\]()…]+", stripped))):
            failures.append(f"line {number}: a line of orphaned punctuation: {stripped[:40]}")
    for number, line in prose_lines(text):
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, fragment = target.partition("#")
            if path and not (ROOT / path).exists():
                failures.append(f"line {number}: link to {path}, which does not exist")
            elif not path and fragment not in slugs:
                failures.append(f"line {number}: anchor #{fragment} matches no heading")
    failures += unescaped_tags(text, DOCUMENT.name)
    for block in re.finditer(r"(?ms)^```json\n(.*?)^```", text):
        if not parses(block.group(1)) and not parses("{" + block.group(1) + "}"):
            line = text[:block.start()].count("\n") + 1
            failures.append(f"line {line}: a json block does not parse")
    document, load_failures = load(V31 / "sentences.json")
    if document is None:
        return failures + load_failures
    bodies = chapter_bodies(text)
    renderer = load_renderer()
    for entry in document["sentences"]:
        chapter = renderer.CHAPTER_OF_PART[entry["part"]]
        if plain(entry["sentence"]) not in plain(bodies.get(chapter, "")):
            failures.append(f"{entry['id']} (part {entry['part']}, {entry['section']}) is not in "
                            f"chapter {chapter}: {entry['sentence'][:70]}")
    table = [line for line in bodies.get(SENTENCES_CHAPTER, "").splitlines() if line.startswith("|")]
    expected_rows = [(e["id"], e["sentence"], e["audience"]) for e in document["sentences"]]
    if renderer.parse(renderer.render(document["sentences"])) != expected_rows:
        failures.append("scripts/render-sentences.py does not round-trip the sentences")
    if table != renderer.render(document["sentences"]).splitlines():
        failures.append(f"chapter {SENTENCES_CHAPTER}'s table is not what scripts/render-sentences.py prints")
    failures += check_chapter_cells(text, table)
    return failures + check_dialect_document({e["sentence"] for e in document["sentences"]})


def check_dialect_document(known_sentences):
    """The versioned dialect: it names its version, its links resolve, every sentence it quotes is the design's."""
    if not DIALECT_DOCUMENT.exists():
        return [f"{DIALECT_DOCUMENT.relative_to(ROOT)}: missing"]
    text = DIALECT_DOCUMENT.read_text(encoding="utf-8")
    where = DIALECT_DOCUMENT.relative_to(ROOT)
    failures = []
    if DIALECT_VERSION not in text:
        failures.append(f"{where}: never names {DIALECT_VERSION}")
    for number, line in prose_lines(text):
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, fragment = target.partition("#")
            if path and not (DIALECT_DOCUMENT.parent / path).resolve().exists():
                failures.append(f"{where} line {number}: link to {path}, which does not exist")
    for marker in ("/blob/main/", "/tree/main/"):
        if marker in text:
            failures.append(f"{where}: a link contains {marker}")
    failures += unescaped_tags(text, str(where))
    known = {plain(sentence) for sentence in known_sentences} | {plain(sentence) for sentence in area_sentences()}
    quoted = re.findall(r'\*"(.*?)"\*', text)
    if not quoted:
        failures.append(f"{where}: quotes no sentence")
    for sentence in quoted:
        if plain(sentence) not in known:
            failures.append(f"{where}: quotes a sentence that is not in sentences.json or the suite's area sentences: {sentence[:70]}")
    return failures


AREA_SENTENCE_ROW = re.compile(r'^\| `A\d{2}-\d{3}` \| \*"(.*?)"\* \|')


def area_sentences():
    """This implementation's area sentences (A<area>-<n>), as the conformance README's tables quote them."""
    readme = V31 / "conformance" / "README.md"
    return [match.group(1) for line in readme.read_text(encoding="utf-8").splitlines()
            if (match := AREA_SENTENCE_ROW.match(line))]


def conformance_table_rows(chapter):
    """Chapter 12's suite table, by family id: the Lives-at cell and the Exported-by cell."""
    rows = {}
    for line in chapter.splitlines():
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) == 4 and re.fullmatch(r"`[a-z-]+`", cells[1]):
            rows[cells[1].strip("`")] = (cells[2], cells[3])
    return rows


def check_conformance_index():
    """Chapter 12's suite: the index names real cases, lists `schemas`' example files exactly, and follows chapter 12's table."""
    path = V31 / "conformance" / "index.json"
    document, failures = load(path)
    if document is None:
        return failures
    families = document.get("families", [])
    ids = [family.get("id") for family in families]
    if len(set(ids)) != len(ids):
        failures.append(f"{path.relative_to(ROOT)}: a family id is repeated")
    for family in families:
        for case in family.get("cases", []):
            # A case is a file (a schema's example) or a folder (a refusal package's valid/ or invalid/).
            if not (ROOT / family.get("path", "") / case).exists():
                failures.append(f"family {family.get('id')}: case {case} is not a file or folder under {family.get('path')}")
        if family.get("id") == "schemas":
            on_disk = sorted(str(file.relative_to(CONFORMANCE)) for file in CONFORMANCE.rglob("*.json"))
            expect(failures, "the schemas family's cases (the example files on disk)",
                   sorted(family.get("cases", [])), on_disk)
    if "schemas" not in ids:
        failures.append("the index has no schemas family")
    chapter = chapter_bodies(DOCUMENT.read_text(encoding="utf-8")).get(CONFORMANCE_CHAPTER, "")
    rows = conformance_table_rows(chapter)
    positions = [chapter.find(f"| `{id_}` |") for id_ in ids]
    if -1 in positions or positions != sorted(positions) or sorted(rows) != sorted(ids):
        failures.append(f"chapter {CONFORMANCE_CHAPTER}'s table does not list the index's families in order: {ids}")
    for family in families:
        lives_at, exported_by = rows.get(family.get("id"), ("", ""))
        where = family.get("path", "").rstrip("/")
        if not any(token.startswith(where) for token in re.findall(r"`([^`]+)`", lives_at)):
            failures.append(f"family {family.get('id')}: path {where} is not in chapter {CONFORMANCE_CHAPTER}'s Lives-at cell")
        expect(failures, f"family {family.get('id')}'s exportedBy against chapter {CONFORMANCE_CHAPTER}'s table",
               family.get("exportedBy"), exported_by.replace(" (here, now)", ""))
    return failures


REFUSAL_PACKAGES = V31 / "conformance" / "refusal-packages"
AREA_SENTENCE_ID = re.compile(r"^A\d{2}-\d{3}$")
EXPECT_KEYS = ["about", "valid", "sentences"]
# The one case whose package has no manifest.json: its sentence is about that absence.
WITHOUT_MANIFEST = {"A02-003/invalid"}


def sentence_pattern(id_, row):
    """A row of sentences.json as a pattern: literal text escaped; each outermost <…> (nested ones, and
    <a | b> choices, as one) any text, non-greedy. S04-009's first word may be any flow kind's, as
    chapter 4 says ("also While, If, Case")."""
    pattern, literal, depth = "", "", 0
    for character in row:
        if character == "<":
            if depth == 0:
                pattern += re.escape(literal) + ".+?"
                literal = ""
            depth += 1
        elif character == ">" and depth > 0:
            depth -= 1
        elif depth == 0:
            literal += character
    pattern += re.escape(literal)
    if id_ == "S04-009":
        pattern = "(?:Loop|While|If|Case)" + pattern[len(re.escape("Loop")):]
    return pattern


def expand_fragments(rows):
    """Two rows of chapter 5 are written as fragments of another's ("the rest unchanged"): S05-025 is
    S05-024's with the run-dependent <value> in place of run.<fact> (R-R5), and S05-043 is S05-042's with
    part.<name> in place of its macro (R-M1). Each is matched as the whole sentence it stands for, as the
    library's tests read it."""
    rows = dict(rows)
    if rows.get("S05-025", "").startswith("\u2026") and "S05-024" in rows:
        rows["S05-025"] = rows["S05-024"].replace(
            " and run.<fact> in one output ", " and the run-dependent <value> in one output ")
    if rows.get("S05-043", "").endswith("\u2026") and "; " in rows.get("S05-042", ""):
        full = rows["S05-042"]
        rows["S05-043"] = rows["S05-043"][:-1] + full[full.index("; ") + 2:]
    return rows


def check_refusal_packages():
    """Chapter 12 § 12.3's refusal packages: the family lists exactly the case folders on disk; each
    expect.json is { about, valid, sentences }, valid as its folder says; in an invalid case whose id
    has a row of sentences.json, each sentence is the row of some published id and one is the case's
    own, as a pattern (an A<area>-<n> case is this implementation's sentence, judged by shape only);
    every package has its manifest.json."""
    index, failures = load(V31 / "conformance" / "index.json")
    document, errors = load(V31 / "sentences.json")
    failures += errors
    if index is None or document is None:
        return failures
    rows = expand_fragments({entry["id"]: entry["sentence"] for entry in document.get("sentences", [])})
    patterns = {row_id: sentence_pattern(row_id, row) for row_id, row in rows.items()}
    family = next((f for f in index.get("families", []) if f.get("id") == "refusal-packages"), None)
    if family is None:
        return failures + ["the index has no refusal-packages family"]

    on_disk = sorted(f"{case.name}/{side.name}"
                     for case in (REFUSAL_PACKAGES.iterdir() if REFUSAL_PACKAGES.is_dir() else [])
                     if case.is_dir() for side in case.iterdir() if side.is_dir())
    expect(failures, "the refusal-packages family's cases (the case folders on disk)",
           sorted(family.get("cases", [])), on_disk)
    for case in on_disk:
        id_, side = case.split("/")
        where = f"refusal-packages/{case}"
        if side not in ("valid", "invalid"):
            failures.append(f"{where}: a case folder is valid/ or invalid/")
            continue
        if id_ not in rows and not AREA_SENTENCE_ID.match(id_):
            failures.append(f"{where}: {id_} is neither a row of sentences.json nor an area's sentence")
        if case not in WITHOUT_MANIFEST and not (REFUSAL_PACKAGES / case / "package" / "manifest.json").is_file():
            failures.append(f"{where}: no package/manifest.json")
        expected, errors = load(REFUSAL_PACKAGES / case / "expect.json")
        failures += errors
        if expected is None:
            continue
        if not isinstance(expected, dict) or list(expected) != EXPECT_KEYS:
            failures.append(f"{where}/expect.json: expected exactly {EXPECT_KEYS}")
            continue
        about, valid, sentences = (expected[key] for key in EXPECT_KEYS)
        if not isinstance(about, str) or not about.strip():
            failures.append(f"{where}/expect.json: about is not a non-empty string")
        if valid is not (side == "valid"):
            failures.append(f"{where}/expect.json: valid is {valid!r} in a {side}/ folder")
        if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
            failures.append(f"{where}/expect.json: sentences is not a list of strings")
            continue
        if (side == "valid") == bool(sentences):
            failures.append(f"{where}/expect.json: a valid package says no sentence, an invalid one at least one")
        # A case that cannot break its rule alone lists every sentence the parser gives: each is some
        # published row's, and one is its own.
        if side == "invalid" and id_ in rows and sentences:
            for sentence in sentences:
                if not any(re.fullmatch(p, sentence, re.DOTALL) for p in patterns.values()):
                    failures.append(f"{where}/expect.json: a sentence is no published row's: {sentence[:70]}")
            if not any(re.fullmatch(patterns[id_], sentence, re.DOTALL) for sentence in sentences):
                failures.append(f"{where}/expect.json: no sentence is {id_}'s row: {sentences[0][:70]}")
    return failures


# Chapter 3's goldens and vectors (area 04): each family's case members, in order.
VECTOR_FAMILIES = {
    "operation-goldens": ["about", "rule", "data", "output"],
    "printer-goldens": ["about", "rule", "text"],
    "null-vectors": ["about", "rule", "data", "result"],
    "text-vectors": ["about", "rule", "data", "result"],
    "number-vectors": ["about", "rule", "data", "result"],
    "date-vectors": ["about", "rule", "data", "result"],
}
VECTOR_FILE_KEYS = ["about", "cases"]


def check_vectors():
    """Chapter 3's goldens and vectors: each family lists exactly the JSON files in its folder, and
    operation-goldens has one file per custom operation; each file is { about, cases }, a non-empty list;
    each case has its family's members, in order: a non-empty about, a rule, an object of data, and an
    output (a string of JSON), a text (a string) or a result."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    families = {family.get("id"): family for family in index.get("families", [])}
    for id_, members in VECTOR_FAMILIES.items():
        family = families.get(id_)
        if family is None:
            failures.append(f"the index has no {id_} family")
            continue
        folder = ROOT / family.get("path", "")
        on_disk = sorted(path.name for path in folder.glob("*")) if folder.is_dir() else []
        expect(failures, f"the {id_} family's cases (the files on disk)", sorted(family.get("cases", [])), on_disk)
        if id_ == "operation-goldens":
            expect(failures, "the operation goldens (one file per custom operation)",
                   on_disk, sorted(f"{name}.json" for name in OPERATIONS))
        for name in on_disk:
            where = f"{id_}/{name}"
            document, errors = load(folder / name)
            failures += errors
            if document is None:
                continue
            if not isinstance(document, dict) or list(document) != VECTOR_FILE_KEYS:
                failures.append(f"{where}: expected exactly {VECTOR_FILE_KEYS}")
                continue
            if not isinstance(document["about"], str) or not document["about"].strip():
                failures.append(f"{where}: about is not a non-empty string")
            cases = document["cases"]
            if not isinstance(cases, list) or not cases:
                failures.append(f"{where}: cases is not a non-empty list")
                continue
            for number, case in enumerate(cases, 1):
                at = f"{where} case {number}"
                if not isinstance(case, dict) or list(case) != members:
                    failures.append(f"{at}: expected exactly {members}")
                    continue
                if not isinstance(case["about"], str) or not case["about"].strip():
                    failures.append(f"{at}: about is not a non-empty string")
                if "data" in case and not isinstance(case["data"], dict):
                    failures.append(f"{at}: data is not an object")
                if "text" in case and not isinstance(case["text"], str):
                    failures.append(f"{at}: text is not a string")
                if "output" in case:
                    if not isinstance(case["output"], str):
                        failures.append(f"{at}: output is not a string")
                    elif not parses_as_json(case["output"]):
                        failures.append(f"{at}: output is not JSON text")
    return failures


COMPILED_DOCUMENTS = V31 / "conformance" / "compiled-documents"
COMPILED_CASE_FILES = ["about.txt", "lock.json", "resolve.json", "toolchain.json"]


def check_compiled_documents():
    """Chapter 7's compiled documents (area 05): the family lists exactly the case folders on disk; each case holds
    source/ (with its manifest.json), toolchain.json, resolve.json, lock.json and about.txt; resolve.json validates
    against resolve.schema.json and lock.json against lock.schema.json; and lock.json's resolve.hash is the SHA-256
    of resolve.json's bytes."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    family = next((f for f in index.get("families", []) if f.get("id") == "compiled-documents"), None)
    if family is None:
        return failures + ["the index has no compiled-documents family"]
    on_disk = sorted(case.name for case in COMPILED_DOCUMENTS.iterdir() if case.is_dir()) \
        if COMPILED_DOCUMENTS.is_dir() else []
    expect(failures, "the compiled-documents family's cases (the case folders on disk)",
           sorted(family.get("cases", [])), on_disk)

    registry, errors = build_registry()
    failures += errors
    validators = {name: validator_for(schema_for(name), registry, failures) for name in ("resolve", "lock")}
    for case in on_disk:
        folder = COMPILED_DOCUMENTS / case
        where = f"compiled-documents/{case}"
        files = sorted(path.name for path in folder.iterdir() if path.is_file())
        expect(failures, f"{where}: its files", files, COMPILED_CASE_FILES)
        if not (folder / "source" / "manifest.json").is_file():
            failures.append(f"{where}: no source/manifest.json")
        documents = {}
        for name in ("resolve", "lock"):
            document, errors = load(folder / f"{name}.json")
            failures += errors
            if document is None:
                continue
            documents[name] = document
            validator = validators[name]
            if validator is not None:
                for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
                    failures.append(f"{where}/{name}.json: {error.message[:100]} at {list(error.absolute_path)}")
        if "lock" in documents and (folder / "resolve.json").is_file():
            digest = "sha256:" + hashlib.sha256((folder / "resolve.json").read_bytes()).hexdigest()
            expect(failures, f"{where}/lock.json: resolve.hash (the SHA-256 of resolve.json's bytes)",
                   (documents["lock"].get("resolve") or {}).get("hash"), digest)
    return failures


MIGRATION_VECTORS = V31 / "conformance" / "migration-vectors"
MIGRATION_CASE_FILES = ["about.txt", "notices.json", "options.json"]
MIGRATION_CASE_FOLDERS = ["expected", "source"]
MIGRATION_OPTIONS_KEYS = ["renames", "whenEmpty", "folderFormats", "toolchain"]
MIGRATION_TOOLCHAIN_KEYS = ["packageFormat", "dialect", "libraries", "evaluator", "runtime", "catalogues"]
MIGRATION_NOTICES_KEYS = ["notices", "handEdits", "refusals"]
SNAPSHOT_TEST = "tests/migration_snapshot.json"


def check_migration_vectors():
    """Chapter 10's migration vectors (area 10): the family lists exactly the case folders on disk; each case holds
    source/, expected/, options.json, notices.json and about.txt, and nothing else; source/manifest.json declares
    specVersion 30 and expected/manifest.json 31; options.json has its four members in order, each hand choice null or
    an object of strings and the toolchain in lock.json's names; notices.json has its three members in order, each a
    list of strings, its hand edits among its notices in their order, and no refusal; a case with a hand edit has no
    snapshot test, and every expected/tests/migration_snapshot.json validates against test.schema.json."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    on_disk = sorted(case.name for case in MIGRATION_VECTORS.iterdir() if case.is_dir()) \
        if MIGRATION_VECTORS.is_dir() else []
    expect(failures, "the migration-vectors family's cases (the case folders on disk)",
           family_cases(index, "migration-vectors", failures), on_disk)

    registry, errors = build_registry()
    failures += errors
    validator = validator_for(schema_for("test"), registry, failures)
    for case in on_disk:
        folder = MIGRATION_VECTORS / case
        where = f"migration-vectors/{case}"
        expect(failures, f"{where}: its files", sorted(p.name for p in folder.iterdir() if p.is_file()), MIGRATION_CASE_FILES)
        expect(failures, f"{where}: its folders", sorted(p.name for p in folder.iterdir() if p.is_dir()), MIGRATION_CASE_FOLDERS)
        for side, version in (("source", 30), ("expected", 31)):
            manifest, errors = load(folder / side / "manifest.json")
            failures += errors
            if manifest is not None:
                expect(failures, f"{where}/{side}/manifest.json: specVersion", manifest.get("specVersion"), version)

        options, errors = load(folder / "options.json")
        failures += errors
        if options is not None:
            expect(failures, f"{where}/options.json: its members", list(options), MIGRATION_OPTIONS_KEYS)
            for member in MIGRATION_OPTIONS_KEYS[:3]:
                choice = options.get(member)
                if choice is not None and not (isinstance(choice, dict)
                                               and all(isinstance(v, str) for v in choice.values())):
                    failures.append(f"{where}/options.json: {member} is neither null nor an object of strings")
            toolchain = options.get("toolchain")
            expect(failures, f"{where}/options.json: the toolchain's members",
                   list(toolchain) if isinstance(toolchain, dict) else toolchain, MIGRATION_TOOLCHAIN_KEYS)

        notices, errors = load(folder / "notices.json")
        failures += errors
        hand_edits = []
        if notices is not None:
            expect(failures, f"{where}/notices.json: its members", list(notices), MIGRATION_NOTICES_KEYS)
            lists = {key: notices.get(key) for key in MIGRATION_NOTICES_KEYS}
            if not all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in lists.values()):
                failures.append(f"{where}/notices.json: a member is not a list of strings")
            else:
                hand_edits = lists["handEdits"]
                expect(failures, f"{where}/notices.json: handEdits (the notices that are hand edits, in order)",
                       hand_edits, [n for n in lists["notices"] if n in hand_edits])
                if not set(hand_edits) <= set(lists["notices"]):
                    failures.append(f"{where}/notices.json: a hand edit is not among the notices")
                expect(failures, f"{where}/notices.json: refusals (a vector is a package the migration writes)",
                       lists["refusals"], [])

        snapshot = folder / "expected" / SNAPSHOT_TEST
        if hand_edits and snapshot.exists():
            failures.append(f"{where}: has a hand edit and a snapshot test")
        if snapshot.exists():
            document, errors = load(snapshot)
            failures += errors
            if document is not None and validator is not None:
                for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path)):
                    failures.append(f"{where}/expected/{SNAPSHOT_TEST}: {error.message[:100]} at {list(error.absolute_path)}")
    return failures


DIALECT_GOLDENS = V31 / "conformance" / "dialect-goldens"
DIALECT_CASE_FILES = {"about.txt", "scope.json", "placed.json", "expected.txt"}
DIALECT_CASE_OPTIONAL = {"expected.neutral.txt", "reply.txt", "expected.reply.txt"}


def family_cases(index, id_, failures):
    family = next((f for f in index.get("families", []) if f.get("id") == id_), None)
    if family is None:
        failures.append(f"the index has no {id_} family")
        return []
    return sorted(family.get("cases", []))


def text_file(path, where, failures):
    try:
        return path.read_bytes().decode("utf-8")
    except FileNotFoundError:
        failures.append(f"{where}: missing")
    except UnicodeDecodeError:
        failures.append(f"{where}: not UTF-8")
    return None


def check_dialect_goldens():
    """Chapter 5's dialect goldens (area 07): the family lists exactly the case folders on disk; each case holds
    about.txt, scope.json (an object), placed.json (an object of booleans) and expected.txt, and either template.md or
    package/ (with its manifest.json) and entry.txt (one line, the entry composed); expected.neutral.txt, and
    reply.txt with expected.reply.txt, only together and nothing else."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    listed = family_cases(index, "dialect-goldens", failures)
    on_disk = sorted(case.name for case in DIALECT_GOLDENS.iterdir() if case.is_dir()) if DIALECT_GOLDENS.is_dir() else []
    expect(failures, "the dialect-goldens family's cases (the case folders on disk)", listed, on_disk)
    for case in on_disk:
        folder = DIALECT_GOLDENS / case
        where = f"dialect-goldens/{case}"
        files = {path.name for path in folder.iterdir() if path.is_file()}
        folders = {path.name for path in folder.iterdir() if path.is_dir()}
        if "template.md" in files:
            inputs = {"template.md"}
            expect(failures, f"{where}: its folders", sorted(folders), [])
        else:
            inputs = {"entry.txt"}
            expect(failures, f"{where}: its folders", sorted(folders), ["package"])
            if not (folder / "package" / "manifest.json").is_file():
                failures.append(f"{where}: neither template.md nor package/manifest.json")
            entry = text_file(folder / "entry.txt", f"{where}/entry.txt", failures)
            if entry is not None and not re.fullmatch(r"(node|deliverable)(\.[a-z][a-z0-9_]*)+\n", entry):
                failures.append(f"{where}/entry.txt: not one line naming a node's or a deliverable's rooted key")
        missing = sorted((DIALECT_CASE_FILES | inputs) - files)
        extra = sorted(files - DIALECT_CASE_FILES - inputs - DIALECT_CASE_OPTIONAL)
        if missing or extra:
            failures.append(f"{where}: missing {missing}, unexpected {extra}")
        if ("reply.txt" in files) != ("expected.reply.txt" in files):
            failures.append(f"{where}: reply.txt and expected.reply.txt go together")
        for name in sorted(files - {"scope.json", "placed.json"}):
            text = text_file(folder / name, f"{where}/{name}", failures)
            if name == "about.txt" and text is not None and not text.strip():
                failures.append(f"{where}/about.txt: empty")
        scope, errors = load(folder / "scope.json")
        failures += errors
        if scope is not None and not isinstance(scope, dict):
            failures.append(f"{where}/scope.json: not an object")
        placed, errors = load(folder / "placed.json")
        failures += errors
        if placed is not None and not (isinstance(placed, dict) and all(isinstance(v, bool) for v in placed.values())):
            failures.append(f"{where}/placed.json: not an object of booleans")
    return failures


RENDERER_GOLDENS = V31 / "conformance" / "renderer-goldens"
RENDERER_CASE_FILES = ["about.txt", "expected.txt", "value.json"]


def check_renderer_goldens():
    """Chapter 5's built-in renderers (area 07): the family lists exactly the <renderer>/<case> folders on disk, each
    renderer a built-in of v31/renderers/index.json; each case holds exactly about.txt, value.json (an object) and
    expected.txt."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    listed = family_cases(index, "renderer-goldens", failures)
    renderers, errors = load(V31 / "renderers" / "index.json")
    failures += errors
    built_in = set((renderers or {}).get("items", []))
    on_disk = sorted(f"{renderer.name}/{case.name}" for renderer in RENDERER_GOLDENS.iterdir() if renderer.is_dir()
                     for case in renderer.iterdir() if case.is_dir()) if RENDERER_GOLDENS.is_dir() else []
    expect(failures, "the renderer-goldens family's cases (the case folders on disk)", listed, on_disk)
    for case in on_disk:
        folder = RENDERER_GOLDENS / case
        where = f"renderer-goldens/{case}"
        if case.split("/")[0] not in built_in:
            failures.append(f"{where}: {case.split('/')[0]} is no built-in renderer")
        expect(failures, f"{where}: its files", sorted(path.name for path in folder.iterdir()), RENDERER_CASE_FILES)
        value, errors = load(folder / "value.json")
        failures += errors
        if value is not None and not isinstance(value, dict):
            failures.append(f"{where}/value.json: not an object")
        for name in ("about.txt", "expected.txt"):
            text_file(folder / name, f"{where}/{name}", failures)
    return failures


ESCAPE_VECTORS = V31 / "conformance" / "markdown-escape-vectors"
ASCII_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"


LEADING_REFERENCES = {" ": "&#32;", "\t": "&#9;"}


def markdown_escape(plain):
    """markdown_escape 1.0.0: a backslash before each ASCII punctuation character; the first space or tab of each line
    (a line starts at the text's start and after each \\n or \\r) as its character reference."""
    out = []
    for at, c in enumerate(plain):
        if c in LEADING_REFERENCES and (at == 0 or plain[at - 1] in "\n\r"):
            out.append(LEADING_REFERENCES[c])
        elif c in ASCII_PUNCTUATION:
            out.append("\\" + c)
        else:
            out.append(c)
    return "".join(out)


def check_markdown_escape_vectors():
    """Chapter 6's escape (area 07): the family lists exactly the one file on disk, vectors.json, a list of
    { plain, escaped } in that order; it holds each of the 32 ASCII punctuation characters alone, and each escaped is
    its plain with a backslash before each ASCII punctuation character and the first space or tab leading each line (at
    the start, and after each \\n or \\r) written &#32; or &#9; (Consultologist-Blazor#1505, ruling R9), nothing else
    changed."""
    index, failures = load(V31 / "conformance" / "index.json")
    if index is None:
        return failures
    listed = family_cases(index, "markdown-escape-vectors", failures)
    on_disk = sorted(path.name for path in ESCAPE_VECTORS.iterdir()) if ESCAPE_VECTORS.is_dir() else []
    expect(failures, "the markdown-escape-vectors family's cases (the files on disk)", listed, on_disk)
    expect(failures, "the markdown-escape-vectors family's files", on_disk, ["vectors.json"])
    vectors, errors = load(ESCAPE_VECTORS / "vectors.json")
    failures += errors
    if vectors is None:
        return failures
    if not isinstance(vectors, list):
        return failures + ["markdown-escape-vectors/vectors.json: not a list"]
    plains = []
    for number, vector in enumerate(vectors, 1):
        where = f"markdown-escape-vectors/vectors.json vector {number}"
        if not isinstance(vector, dict) or list(vector) != ["plain", "escaped"] \
                or not all(isinstance(v, str) for v in vector.values()):
            failures.append(f"{where}: expected exactly ['plain', 'escaped'], two strings")
            continue
        plains.append(vector["plain"])
        if vector["escaped"] != markdown_escape(vector["plain"]):
            failures.append(f"{where}: escaped is not plain with a backslash before each ASCII punctuation character "
                            "and each line's first leading space or tab as its character reference")
    missing = [c for c in ASCII_PUNCTUATION if c not in plains]
    if missing:
        failures.append(f"markdown-escape-vectors/vectors.json: no vector of {missing} alone")
    return failures


def parses_as_json(text):
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


# #1508 (ruling 3 of 2026-11-21, and of 2026-11-22 on area 07): every member written into the compiled documents is named.
RULED_ENTRY_MEMBERS = ["plainConverts", "names", "placements", "places", "runSpots", "ret", "renders"]
RULED_DELIVERABLE_MEMBERS = ["delivery", "bundle", "escapes"]
RULED_PLACEMENT_MEMBERS = ["site", "within", "if", "plainConverts", "form"]
RULED_RUN_SPOT_MEMBERS = ["site", "at", "reads", "unit", "neutral"]
RULED_STAMP_MEMBERS = ["specVersion", "resolveHash", "lockHash", "migratedFrom"]
RULED_ENTRY_MEMBERS += ["nodes", "then", "else", "branches"]
# The record members areas 08 and 09 added at 31 (the provenance repository holds the contract; this guards the names).
RULED_RECORD_MEMBERS = [
    # the job header
    "resolveHash", "lockHash", "versionsRan", "recordHash", "runFacts", "limits", "startedAtUtc",
    "signatureBlockId", "signatureChosen", "decisions", "schemaVersion", "effectiveInputHash",
    "effectiveInputHashVersion", "tokens",
    # limits' members
    "maxAgentCalls", "capacityWaitMinutes", "serviceAttempts", "jobMinutes", "deliveryMinutes",
    "deliveryAttempts", "loopItems", "jobAgentCalls", "jobInstances", "renderSteps",
    # rows
    "producer", "modelDerived", "runDependent", "profileCarrying", "sentFormatHash", "failWith",
    "itemId", "positionName", "hashVersion", "deliveries", "textDroppedAtUtc",
]


def named(name, text):
    """Whether text names the member `name`, as `name` or as "name": inside a written example."""
    return f"`{name}`" in text or f'"{name}":' in text


def check_compiled_members():
    """Every member the schemas name in resolve.json's entries (a flat-map entry, a function, a deliverable's own
    members, a placement, a run spot, a render site) is named in chapter 7 § 7.2.5's text, and every member of
    publish.json's stamp in § 7.5's; the ruled members are in the schemas. This repository holds no
    machine-readable list of the record's members (chapter 9 is prose, and no schema describes the record), so the
    record's member names can only be guarded by name: RULED_RECORD_MEMBERS lists those areas 08 and 09 added at 31 and
    chapter 9 must name each. The provenance repository holds the contract and its layout."""
    failures = []
    resolve, errors = load(SCHEMAS / "resolve.schema.json")
    failures += errors
    stamp, errors = load(SCHEMAS / "publish-stamp.schema.json")
    failures += errors
    if resolve is None or stamp is None:
        return failures
    definitions = resolve.get("$defs", {})
    deliverable = next((part.get("properties", {}) for part in definitions.get("deliverable", {}).get("allOf", [])
                        if "properties" in part), {})
    groups = {
        "entry": definitions.get("entry", {}).get("properties", {}),
        "function": definitions.get("function", {}).get("properties", {}),
        "deliverable": deliverable,
        "placement": definitions.get("placement", {}).get("properties", {}),
        "runSpot": definitions.get("runSpot", {}).get("properties", {}),
        "renderSite": definitions.get("renderSite", {}).get("properties", {}),
    }
    for group, ruled in [("entry", RULED_ENTRY_MEMBERS), ("deliverable", RULED_DELIVERABLE_MEMBERS),
                         ("placement", RULED_PLACEMENT_MEMBERS), ("runSpot", RULED_RUN_SPOT_MEMBERS)]:
        for name in ruled:
            if name not in groups[group]:
                failures.append(f"resolve.schema.json $defs.{group}: the ruled member '{name}' is not named")
    expect(failures, "publish-stamp.schema.json's members", sorted(stamp.get("properties", {})), sorted(RULED_STAMP_MEMBERS))
    if "derivedFrom" not in resolve.get("properties", {}):
        failures.append("resolve.schema.json: the ruled member 'derivedFrom' is not named")

    sections = [section for section in heading_sections(DOCUMENT.read_text(encoding="utf-8")) if section[0] == 7]
    texts = {title: text for _, title, text in sections}
    flat = next((text for title, text in texts.items() if title.startswith("The flat maps")), None)
    pipeline = texts.get("The publish pipeline")
    if flat is None or pipeline is None:
        return failures + ["chapter 7 has no 'The flat maps' or no 'The publish pipeline' section"]
    for group, properties in groups.items():
        for name in properties:
            if not named(name, flat):
                failures.append(f"chapter 7 § 7.2.5 does not name the member `{name}` of resolve.schema.json's {group}")
    for name in stamp.get("properties", {}):
        if not named(name, pipeline):
            failures.append(f"chapter 7 § 7.5 does not name the member `{name}` of the publish stamp")
    # The other way: every member of § 7.2.5's derived-member table has a property in `entry`.
    for row in flat.splitlines():
        cell = row.split("|")[1] if row.startswith("| `") else ""
        for name in re.findall(r"`(\w+)`", cell):
            if name not in groups["entry"]:
                failures.append(f"chapter 7 § 7.2.5's table names the member `{name}`, which resolve.schema.json's entry does not")
    if "`publish.json`" not in pipeline:
        failures.append("chapter 7 § 7.5 does not name the stamp's file, `publish.json`")
    record = chapter_bodies(DOCUMENT.read_text(encoding="utf-8")).get(9, "")
    for name in RULED_RECORD_MEMBERS:
        if not re.search(rf"\b{name}\b", record):
            failures.append(f"chapter 9 does not name the record member {name}")
    return failures


PART_CITATION = re.compile(r"\b[Pp]arts? \d{2}\b")


def check_citations():
    """A reader has the document's chapters, not the design's parts: no JSON under v31/ cites a part.
    The refusal packages' package/ folders are skipped: they are uploads as a reader receives them,
    and may hold bytes that are not UTF-8 or JSON on purpose."""
    failures = []
    for path in sorted(V31.rglob("*.json")):
        relative = path.relative_to(REFUSAL_PACKAGES).parts if path.is_relative_to(REFUSAL_PACKAGES) else ()
        if "package" in relative[2:3]:
            continue
        for match in PART_CITATION.finditer(path.read_text(encoding="utf-8")):
            failures.append(f"{path.relative_to(ROOT)}: cites '{match.group(0)}'; cite the chapter")
    return failures


CHECKS = [("constants", check_constants), ("sentences", check_sentences),
          ("examples", check_examples), ("formats", check_formats),
          ("renderers", check_renderers), ("self", check_self),
          ("conformance", check_conformance_index), ("refusal-packages", check_refusal_packages),
          ("vectors", check_vectors), ("compiled-documents", check_compiled_documents),
          ("migration-vectors", check_migration_vectors),
          ("dialect-goldens", check_dialect_goldens), ("renderer-goldens", check_renderer_goldens),
          ("markdown-escape-vectors", check_markdown_escape_vectors),
          ("compiled-members", check_compiled_members),
          ("document", check_document), ("citations", check_citations)]


def main():
    failed = False
    for name, check in CHECKS:
        failures = check()
        if failures:
            failed = True
            print(f"FAIL {name}")
            for failure in failures:
                print(f"  {failure}")
        else:
            print(f"ok   {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
