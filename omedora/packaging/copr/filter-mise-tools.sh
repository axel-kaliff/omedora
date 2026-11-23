#!/bin/bash
# Split Omarchy's default mise tools by mise-tools-fedora.list.
#
#   filter-mise-tools.sh <omarchy-tools.toml> <list> <kept.toml> <dropped.toml>
#
# kept.toml is the source with the dropped [tools] lines removed; everything
# else (settings, comments) passes through unchanged. dropped.toml holds only
# the dropped declarations under a [tools] header, ready to use as a user
# drop-in. Exits non-zero when a [tools] key is not classified in the list, or
# a listed key no longer exists in the source.

set -euo pipefail

if (( $# != 4 )); then
  echo "Usage: $0 <omarchy-tools.toml> <list> <kept.toml> <dropped.toml>" >&2
  exit 2
fi

source_toml=$1
list=$2
kept=$3
dropped=$4

awk -v kept="$kept" -v dropped="$dropped" '
  FNR == NR {
    if ($1 == "keep" || $1 == "drop") { class[$2] = $1; listed[$2] = 1 }
    next
  }
  FNR == 1 {
    print "# Omarchy'\''s AI coding agent declarations, which omedora-settings leaves out of" >dropped
    print "# /etc/mise/conf.d/omarchy-tools.toml on Fedora (see mise-tools-fedora.list)." >dropped
    print "# Copy a line into ~/.config/mise/conf.d/agents.toml under [tools], or this" >dropped
    print "# whole file into ~/.config/mise/conf.d/, to get those lazy shims back." >dropped
    print "" >dropped
    print "[tools]" >dropped
  }
  /^\[/ { in_tools = ($0 == "[tools]") }
  in_tools && match($0, /^("[^"]+"|[^ =]+) = /) {
    key = substr($0, RSTART, RLENGTH - 3)
    gsub(/"/, "", key)
    seen[key] = 1
    if (!(key in class)) {
      printf "filter-mise-tools: %s is not classified in the list (keep or drop)\n", key >"/dev/stderr"
      bad = 1
    } else if (class[key] == "drop") {
      print >dropped
      next
    }
  }
  { print >kept }
  END {
    for (key in listed) {
      if (!(key in seen)) {
        printf "filter-mise-tools: %s is listed but not declared upstream any more\n", key >"/dev/stderr"
        bad = 1
      }
    }
    exit bad
  }
' "$list" "$source_toml"
