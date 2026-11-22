#!/usr/bin/env bash
# PreToolUse hook for Bash: block destructive rm commands.
# Reads the hook JSON from stdin. Exit 2 blocks the call and shows stderr to Claude.
# Exit 0 allows it.

set -u

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"

# If there is no command (or jq could not parse the input), allow the call.
if [ -z "$command" ]; then
  exit 0
fi

# Match `rm` as a command word (start of line, or after ; & | ( or whitespace).
rm_cmd='(^|[;&|(]|[[:space:]])rm[[:space:]]'

# Recursive and force flags within the same command segment, in any order:
# -rf, -fr, -Rf, -r -f, --recursive --force.
rm_recursive='(-[a-zA-Z]*[rR]|--recursive)'
rm_force='(-[a-zA-Z]*f|--force)'

# Any rm that names habits.json (the runtime data file).
habits_target='habits\.json'

if printf '%s' "$command" | grep -Eq "${rm_cmd}[^;&|]*${rm_recursive}" \
  && printf '%s' "$command" | grep -Eq "${rm_cmd}[^;&|]*${rm_force}"; then
  echo "Blocked: destructive 'rm -rf' command. Delete files one at a time, or ask the user to run it." >&2
  exit 2
fi

if printf '%s' "$command" | grep -Eq "${rm_cmd}.*${habits_target}"; then
  echo "Blocked: habits.json is the user's runtime data and must not be deleted by Claude." >&2
  exit 2
fi

exit 0
