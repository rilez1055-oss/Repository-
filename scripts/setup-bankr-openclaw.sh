#!/usr/bin/env bash
set -euo pipefail

# Bankr + OpenClaw bootstrap for a Linux GitHub Codespace.
# Safe default: does not create write-enabled Bankr credentials or execute trades.

export DEBIAN_FRONTEND=noninteractive

say() { printf '\n==> %s\n' "$*"; }

say "Installing a supported Node.js runtime and OpenClaw"
# OpenClaw's official installer detects the platform and installs a supported Node
# runtime when the current one is too old.
curl -fsSL https://openclaw.ai/install.sh | bash

# Make user-local npm/global bins visible in this shell.
if command -v npm >/dev/null 2>&1; then
  export PATH="$(npm prefix -g)/bin:$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
fi
hash -r 2>/dev/null || true

say "Installing/updating Bankr CLI"
npm install -g @bankr/cli

say "Installing/updating the Bankr skill for OpenClaw"
SKILL_ROOT="${HOME}/.openclaw/workspace/skills/bankr"
mkdir -p "$SKILL_ROOT"
curl -fsSL https://raw.githubusercontent.com/BankrBot/skills/main/bankr/bankr/SKILL.md -o "$SKILL_ROOT/SKILL.md"

say "Checking installed versions"
printf 'Node:    '; node --version
printf 'npm:     '; npm --version
printf 'Bankr:   '; bankr --version
printf 'OpenClaw:'; openclaw --version

say "Checking Bankr authentication"
if ! bankr whoami; then
  cat <<'EOF'

Bankr authentication is not complete in this environment.
Run `bankr login` and finish the browser/OTP authentication.
Do not put a seed phrase or private key into this terminal.
EOF
  exit 2
fi

say "Configuring Bankr LLM Gateway for OpenClaw"
bankr llm setup openclaw --install

say "Verifying Bankr wallet access (read-only)"
bankr wallet portfolio || true

say "Bootstrap complete"
printf '\nInstalled Bankr skill: %s\n' "$SKILL_ROOT/SKILL.md"
printf 'Next read-only checks:\n  bankr whoami\n  bankr wallet portfolio\n'
