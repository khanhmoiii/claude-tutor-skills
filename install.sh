#!/usr/bin/env bash
# Copy the tutor skills into ~/.claude/skills so they run as /learn, /hint, ...
# Existing skills with the same name are skipped unless --force is given.
set -euo pipefail

src="$(cd "$(dirname "$0")" && pwd)/skills"
dst="$HOME/.claude/skills"
mkdir -p "$dst"

for skill in "$src"/*/; do
  name="$(basename "$skill")"
  if [ -e "$dst/$name" ] && [ "${1:-}" != "--force" ]; then
    echo "skip  $name (already exists; rerun with --force to overwrite)"
    continue
  fi
  rm -rf "${dst:?}/${name:?}"
  cp -r "$skill" "$dst/$name"
  echo "ok    $name"
done
echo "Done. Restart Claude Code, then type /learn."
