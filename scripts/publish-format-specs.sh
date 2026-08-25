#!/usr/bin/env bash
# Publish the package-format specifications to the PUBLIC registry and update
# their latest-pointer. The document set is a versioned artifact (spec-versions.json
# declares its own CalVer version); published versions are immutable — this script
# refuses to overwrite an existing version. The engine does not fetch this at
# runtime: it vendors this repo as a submodule and a test asserts its own accepted
# set matches spec-versions.json, so the two cannot silently disagree.
#
# Usage:
#   ./scripts/publish-format-specs.sh <storage-account>
# Example:
#   ./scripts/publish-format-specs.sh consultologistpublic
set -euo pipefail

CONTAINER="package-format"
INDEX="spec-versions.json"

if [[ $# -ne 1 ]]; then
	# 1d drops the shebang, which grep '^#' would otherwise print as usage.
	grep '^#' "$0" | sed -e '1d' -e 's/^# \{0,1\}//' | head -11
	exit 1
fi

ACCOUNT="$1"

[[ -f "$INDEX" ]] || { echo "error: $INDEX not found (run from the repo root)" >&2; exit 1; }

VERSION=$(python3 -c "import json;print(json.load(open('$INDEX'))['version'])")

if ! [[ "$VERSION" =~ ^v[0-9]{4}\.(0[1-9]|1[0-2])\.[1-9][0-9]*$ ]]; then
	echo "error: version '$VERSION' is not vYYYY.MM.N" >&2
	exit 1
fi

AUTH=(--account-name "$ACCOUNT" --auth-mode "${AZ_STORAGE_AUTH_MODE:-login}")

if az storage blob exists "${AUTH[@]}" --container-name "$CONTAINER" \
	--name "$VERSION/$INDEX" --query exists -o tsv | grep -q true; then
	echo "error: package-format@$VERSION is already published; versions are immutable — bump the version" >&2
	exit 1
fi

# Documents first, the index last (a reader resolves the index first, so a
# partial upload is invisible) — the ordering publish-output-contracts.sh uses.
python3 -c "
import json
for f in json.load(open('$INDEX'))['documents'].values(): print(f)
" | sort -u | while read -r DOC; do
	[[ -f "$DOC" ]] || { echo "error: document $DOC named by $INDEX not found" >&2; exit 1; }
	echo "Uploading $VERSION/$DOC"
	az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
		--file "$DOC" --name "$VERSION/$DOC" --output none
done

# The schemas travel with the version too: a schema is a statement about one
# specVersion's shape, and reading it beside a different version's documents
# would be reading the wrong contract.
python3 -c "
import json
for f in json.load(open('$INDEX')).get('schemas', {}).values(): print(f)
" | while read -r SCHEMA; do
	[[ -f "$SCHEMA" ]] || { echo "error: schema $SCHEMA named by $INDEX is missing" >&2; exit 1; }
	echo "Uploading $VERSION/$SCHEMA"
	az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
		--file "$SCHEMA" --name "$VERSION/$SCHEMA" --output none
done

# The conformance suite travels with the version it describes: a case pinned
# to an error message is only meaningful beside the rules that produce it.
if [[ -f conformance/index.json ]]; then
	python3 -c "
import json
for c in json.load(open('conformance/index.json'))['cases']: print('conformance/' + c['path'])
" | while read -r CASE; do
		[[ -f "$CASE" ]] || { echo "error: conformance case $CASE named by the index is missing" >&2; exit 1; }
		az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
			--file "$CASE" --name "$VERSION/$CASE" --output none
	done
	for SUPPORT in conformance/catalog-schemas.json conformance/index.json; do
		echo "Uploading $VERSION/$SUPPORT"
		az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
			--file "$SUPPORT" --name "$VERSION/$SUPPORT" --output none
	done
fi

# The licence travels with the artifact. Somebody who downloads a version out
# of the registry to re-verify a consult should not have to come back to GitHub
# to learn what they may do with it.
echo "Uploading $VERSION/LICENSE"
az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
	--file LICENSE --name "$VERSION/LICENSE" --output none

echo "Uploading $VERSION/$INDEX"
az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
	--file "$INDEX" --name "$VERSION/$INDEX" --output none

echo "Updating latest.json -> $VERSION"
POINTER=$(mktemp)
printf '{"version": "%s"}\n' "$VERSION" > "$POINTER"
az storage blob upload "${AUTH[@]}" --container-name "$CONTAINER" \
	--file "$POINTER" --name "latest.json" --overwrite --output none
rm -f "$POINTER"

echo "Published package-format@$VERSION and updated latest pointer."
