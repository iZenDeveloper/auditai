# Agent instructions — AuditAI

You are working on **AuditAI** (repo `iZenDeveloper/auditai`): LLM/RAG CI quality gates + open-source GTM.

## Start here

1. **GTM / guerrilla continuation:** read [`docs/gtm/HANDOFF_CODEX.md`](docs/gtm/HANDOFF_CODEX.md) end-to-end.  
2. Then sync live state: [`docs/gtm/STATUS.md`](docs/gtm/STATUS.md), [`docs/gtm/TARGETS.md`](docs/gtm/TARGETS.md).  
3. Product overview: root [`README.md`](README.md).

## Non-negotiables

- No secrets in commits or PR bodies. Tokens: `~/.config/github_token`, xAI/OpenAI env, `~/.config/pypi_token`.  
- Guerrilla: **public docs only**, weak mock, honest metrics, badge **opt-in**.  
- PyPI package name is **`auditai-cli`**; CLI/import remain **`auditai`**.  
- Prefer depth + maintainer unblocks over opening many PRs.  
- After external GitHub actions: update `STATUS.md` + `docs/gtm/out/pr_log.jsonl`.

## Quick commands

```bash
pip install -e ".[dev,pdf]" && pytest -q
export GITHUB_TOKEN="$(cat ~/.config/github_token)"
python scripts/gtm/open_guerrilla_pr.py --repo owner/name --judge xai --model grok-4.3 --yes
```

See handoff for follow-up quiet windows, viparse lesson (no pure loaders), and next target **towardsai/ai-tutor-app**.
