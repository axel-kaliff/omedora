echo "Take the AI coding agents' mise shims off PATH on Fedora"

[[ "$(omarchy-distro)" == "fedora" ]] || exit 0
omarchy-cmd-present mise || exit 0

# omedora-settings no longer declares Omarchy's AI coding agents in
# /etc/mise/conf.d/omarchy-tools.toml, or the claude/codex/grok account wrappers
# (omedora/packaging/copr/mise-tools-fedora.list). Their lazy shims stay in this
# user's shims dir until the next reshim, still ahead of ~/.local/bin and
# /usr/bin on PATH. A reshim from the new declarations removes them. Installs
# under ~/.local/share/mise/installs are left alone.
#
# The agent chosen in Setup > Defaults > Agent is the user's own pick, so it
# keeps its shim: its upstream declaration is copied into the user's mise
# config before the reshim.
reference="$OMARCHY_PATH/etc-overrides/mise/conf.d/omarchy-agent-tools.toml"
dropin="$HOME/.config/mise/conf.d/omedora-default-agent.toml"
agent=$(omarchy-default-agent 2>/dev/null || true)

if [[ -n $agent && -f $reference && ! -e $dropin ]]; then
  # The menu stores the agent's command; two agents' mise tools have other names.
  case $agent in
  agy) tool="antigravity-cli" ;;
  omp) tool="oh-my-pi" ;;
  *) tool=$agent ;;
  esac

  declaration=$(awk -v tool="$tool" '
    match($0, /^("[^"]+"|[^ =]+) = /) {
      key = substr($0, RSTART, RLENGTH - 3)
      gsub(/"/, "", key)
      if (key == tool || index($0, "lazy_bins = [\"" tool "\"]")) { print; exit }
    }
  ' "$reference")

  if [[ -n $declaration ]]; then
    mkdir -p "${dropin%/*}"
    printf '%s\n' \
      "# Your default coding agent (Setup > Defaults > Agent), kept when Omedora stopped" \
      "# declaring every AI coding agent for all users. Delete this file to drop its shim." \
      "[tools]" \
      "$declaration" >"$dropin"
  fi
fi

MISE_OFFLINE=true mise reshim --system || true
MISE_OFFLINE=true mise reshim || true
