#!/usr/bin/env python3
"""Checks the specVersion 31 preview files. Exits 0 when every group passes, 1 otherwise.

Each group is a function check_<group>() -> list[str] of failures, registered in CHECKS.
"""
import json
import sys
from pathlib import Path

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
        markdig = constants.get("markdig", {})
        expect(failures, "constants.markdig keys", list(markdig), ["version", "extensions"])
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


CHECKS = [("constants", check_constants)]


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
