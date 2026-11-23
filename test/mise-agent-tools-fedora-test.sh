#!/bin/bash
#
# L1: no AI coding agent is declared system-wide on Fedora.
#
# Omarchy declares every agent CLI as a lazy mise tool in
# etc/mise/conf.d/omarchy-tools.toml, plus claude/codex/grok wrappers in
# omarchy-agent-accounts.toml. On Fedora that would put a shim per agent ahead
# of ~/.local/bin and /usr/bin on every user's PATH. omedora-settings filters
# the tools file through omedora/packaging/copr/mise-tools-fedora.list and
# ships the agents and wrappers only as reference copies. migrations/1795404424.sh
# retires existing shims, keeping the user's chosen default agent.
#
# This test checks:
#   - every upstream tool is classified, and the filter splits them exactly;
#   - every mise-backed agent the Setup > Defaults > Agent menu offers is dropped,
#     so a new upstream agent can't arrive on PATH unnoticed;
#   - the spec installs neither agents nor wrappers in /etc;
#   - the migration's behavior on Arch and Fedora, with and without a default agent.

set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
. "$ROOT/test/helpers.sh"
cd "$ROOT"

COPR="$ROOT/omedora/packaging/copr"
filter="$COPR/filter-mise-tools.sh"
list="$COPR/mise-tools-fedora.list"
spec="$COPR/omedora-settings.spec"
upstream="$ROOT/etc/mise/conf.d/omarchy-tools.toml"
migration="$ROOT/migrations/1795404424.sh"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

tool_keys() {
  awk '
    /^\[/ { in_tools = ($0 == "[tools]"); next }
    in_tools && match($0, /^("[^"]+"|[^ =]+) = /) {
      key = substr($0, RSTART, RLENGTH - 3)
      gsub(/"/, "", key)
      print key
    }
  ' "$1" | sort
}

# --- the filter ---------------------------------------------------------------
"$filter" "$upstream" "$list" "$TMP/kept.toml" "$TMP/dropped.toml" \
  || fail "every Omarchy mise tool is classified keep or drop in mise-tools-fedora.list"
pass "every Omarchy mise tool is classified keep or drop in mise-tools-fedora.list"

assert_equals "kept tools are exactly the list's keep entries" \
  "$(tool_keys "$TMP/kept.toml" | tr '\n' ' ')" "$(awk '$1 == "keep" { print $2 }' "$list" | sort | tr '\n' ' ')"
assert_equals "dropped declarations are exactly the list's drop entries" \
  "$(tool_keys "$TMP/dropped.toml" | tr '\n' ' ')" "$(awk '$1 == "drop" { print $2 }' "$list" | sort | tr '\n' ' ')"
assert_equals "the split loses and invents no tool" \
  "$( { tool_keys "$TMP/kept.toml"; tool_keys "$TMP/dropped.toml"; } | sort | tr '\n' ' ')" \
  "$(tool_keys "$upstream" | tr '\n' ' ')"
assert_equals "the kept file keeps upstream's [settings] unchanged" \
  "$(sed -n '/^\[settings\]/,/^$/p' "$TMP/kept.toml")" "$(sed -n '/^\[settings\]/,/^$/p' "$upstream")"

printf '[tools]\nbrand-new-agent = { version = "latest", lazy = true }\n' >"$TMP/new.toml"
if "$filter" "$TMP/new.toml" "$list" "$TMP/k2" "$TMP/d2" 2>"$TMP/err"; then
  fail "the filter fails on an unclassified tool"
fi
assert_output_contains "the filter names the unclassified tool" "$(cat "$TMP/err")" "brand-new-agent"

# --- every menu agent is dropped ------------------------------------------------
# The migration's own lookup, so the test also covers its agent -> tool names.
lookup() {
  case $1 in agy) tool="antigravity-cli" ;; omp) tool="oh-my-pi" ;; *) tool=$1 ;; esac
  awk -v tool="$tool" '
    match($0, /^("[^"]+"|[^ =]+) = /) {
      key = substr($0, RSTART, RLENGTH - 3)
      gsub(/"/, "", key)
      if (key == tool || index($0, "lazy_bins = [\"" tool "\"]")) { print; exit }
    }
  ' "$2"
}
grep -q 'case \$agent in' "$migration" && grep -q 'agy) tool="antigravity-cli"' "$migration" \
  && grep -q 'omp) tool="oh-my-pi"' "$migration" \
  || fail "the migration maps agy and omp to their mise tools as this test does"

menu_agents=$(grep -oE '"setup\.default\.agent\.[a-z0-9-]+"' default/omarchy/omarchy-menu.jsonc | sed -E 's/"setup\.default\.agent\.(.*)"/\1/' | sort -u)
[[ -n $menu_agents ]] || fail "the menu lists default agents"
for agent in $menu_agents; do
  # OpenClaw and Hermes install through their own installers, not mise.
  [[ $agent == openclaw || $agent == hermes ]] && continue
  [[ -n $(lookup "$agent" "$TMP/dropped.toml") ]] \
    || fail "menu agent $agent is a dropped declaration (not a shim on Fedora)"
  [[ -z $(lookup "$agent" "$TMP/kept.toml") ]] \
    || fail "menu agent $agent is not declared in /etc on Fedora"
done
pass "every mise-backed menu agent is dropped from the system declarations"

# --- the spec --------------------------------------------------------------------
grep -qF 'omedora/packaging/copr/filter-mise-tools.sh etc/mise/conf.d/omarchy-tools.toml' "$spec" \
  || fail "omedora-settings builds omarchy-tools.toml through the filter"
pass "omedora-settings builds omarchy-tools.toml through the filter"
if grep -qE '%\{_sysconfdir\}/mise/conf.d/omarchy-agent-accounts.toml' "$spec"; then
  fail "omedora-settings does not install the agent-account wrappers in /etc"
fi
pass "omedora-settings does not install the agent-account wrappers in /etc"
grep -qF 'etc-overrides/mise/conf.d/omarchy-agent-accounts.toml' "$spec" \
  && grep -qF 'etc-overrides/mise/conf.d/omarchy-agent-tools.toml' "$spec" \
  || fail "the agents and wrappers ship as reference copies"
pass "the agents and wrappers ship as reference copies"

# --- the migration ---------------------------------------------------------------
assert_equals "migration is mode 0644" "$(stat -c %a "$migration")" "644"
head -n1 "$migration" | grep -q '^echo "' || fail "migration starts with a one-line description echo"
pass "migration starts with a one-line description echo"

stub_bin="$TMP/bin"
mkdir -p "$stub_bin" "$TMP/omarchy/etc-overrides/mise/conf.d"
cp "$TMP/dropped.toml" "$TMP/omarchy/etc-overrides/mise/conf.d/omarchy-agent-tools.toml"
cat >"$stub_bin/omarchy-distro" <<'EOF'
#!/bin/bash
echo "$STUB_DISTRO"
EOF
cat >"$stub_bin/omarchy-cmd-present" <<'EOF'
#!/bin/bash
command -v "$1" >/dev/null
EOF
cat >"$stub_bin/omarchy-default-agent" <<'EOF'
#!/bin/bash
[[ -n ${STUB_AGENT:-} ]] && echo "$STUB_AGENT"
exit 0
EOF
cat >"$stub_bin/mise" <<'EOF'
#!/bin/bash
echo "MISE_OFFLINE=${MISE_OFFLINE:-} mise $*" >>"$TEST_CALLS"
EOF
chmod +x "$stub_bin"/*

run_migration() { # distro agent
  rm -rf "$TMP/home" "$TMP/calls"
  mkdir -p "$TMP/home"
  : >"$TMP/calls"
  ( export PATH="$stub_bin:/usr/bin:/bin" HOME="$TMP/home" OMARCHY_PATH="$TMP/omarchy" \
      TEST_CALLS="$TMP/calls" STUB_DISTRO="$1" STUB_AGENT="$2"
    bash -euo pipefail "$migration" ) >"$TMP/out" 2>&1
}
dropin="$TMP/home/.config/mise/conf.d/omedora-default-agent.toml"

run_migration arch kimi || fail "the migration exits 0 on Arch"
assert_equals "on Arch the migration runs no mise" "$(cat "$TMP/calls")" ""
[[ ! -e $dropin ]] || fail "on Arch the migration writes no drop-in"
pass "on Arch the migration does nothing"

run_migration fedora "" || fail "the migration exits 0 on Fedora with no default agent"
assert_equals "on Fedora the migration reshims offline, system then user" "$(cat "$TMP/calls")" \
  "$(printf '%s\n' 'MISE_OFFLINE=true mise reshim --system' 'MISE_OFFLINE=true mise reshim')"
[[ ! -e $dropin ]] || fail "with no default agent the migration keeps no agent"
pass "with no default agent the migration only reshims"

run_migration fedora kimi || fail "the migration exits 0 on Fedora with kimi as the default agent"
assert_file_exists "the default agent keeps its declaration in the user's mise config" "$dropin"
assert_output_contains "the drop-in declares kimi's upstream tool" "$(cat "$dropin")" '"npm:@moonshot-ai/kimi-code" = {'
assert_equals "the drop-in declares only the default agent" "$(tool_keys "$dropin" | tr '\n' ' ')" "npm:@moonshot-ai/kimi-code "

run_migration fedora omp || fail "the migration exits 0 with omp as the default agent"
assert_equals "omp keeps oh-my-pi" "$(tool_keys "$dropin" | tr '\n' ' ')" "oh-my-pi "

# A drop-in the user already has, or edited, is theirs.
rm -rf "$TMP/home"; mkdir -p "$(dirname "$dropin")"
printf 'mine\n' >"$dropin"
( export PATH="$stub_bin:/usr/bin:/bin" HOME="$TMP/home" OMARCHY_PATH="$TMP/omarchy" \
    TEST_CALLS="$TMP/calls" STUB_DISTRO=fedora STUB_AGENT=claude
  bash -euo pipefail "$migration" ) >"$TMP/out" 2>&1 || fail "the migration exits 0 next to an existing drop-in"
assert_equals "an existing drop-in is left alone" "$(cat "$dropin")" "mine"

echo "# all Fedora mise agent-tools tests passed"
