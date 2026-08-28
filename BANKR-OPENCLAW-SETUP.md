# Bankr + OpenClaw setup

This repository contains an automated bootstrap for a Linux/GitHub Codespace.

## Run

```bash
bash scripts/setup-bankr-openclaw.sh
```

The script:

1. Uses the official OpenClaw installer so an OpenClaw-supported Node runtime is installed when needed.
2. Installs the Bankr CLI.
3. Installs the Bankr `SKILL.md` into the OpenClaw workspace skills directory.
4. Verifies Node, npm, Bankr, and OpenClaw.
5. Checks Bankr authentication.
6. Runs `bankr llm setup openclaw --install`.
7. Performs a read-only `bankr wallet portfolio` check.

It does **not** enable write access, execute trades, or create transactions.

## Bankr skill source

The skill is fetched from:

`https://github.com/BankrBot/skills/tree/main/bankr/bankr`

## Safety

Never put seed phrases, private keys, recovery phrases, or API secrets into this repository. Authentication happens through the Bankr CLI/environment.
