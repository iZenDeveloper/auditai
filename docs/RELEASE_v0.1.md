# Release checklist — AuditAI `v0.1.0`

Use this document once. Tick items in order.  
**Current repo state (pre-checklist):** no git commits yet · version already `0.1.0` in `pyproject.toml` · local tests green.

**Locked for this release:**

| Placeholder | Value |
|-------------|--------|
| `OWNER` | `iZenDeveloper` |
| `REPO` | `auditai` |
| `GIT_REMOTE` | `https://github.com/iZenDeveloper/auditai.git` |
| Action ref | `iZenDeveloper/auditai@v0.1` |

---

## 0. Pre-flight (local)

### 0.1 Clean tree

- [ ] No secrets in tree (`.env`, keys, customer data)
- [ ] `.gitignore` covers: `.venv/`, `node_modules/`, `.next/`, `*.db`, `auditai-out/`, `.env*`
- [ ] Confirm fonts are intentional (~1.4MB DejaVu under `src/auditai/fonts/` and `cloud/api/app/fonts/`)

```bash
cd /path/to/auditai
# quick secret scan (should be empty / only false positives)
rg -n "sk-[a-zA-Z0-9]{10,}|aai_[A-Za-z0-9_-]{20,}|OPENAI_API_KEY=.+" \
  --glob '!.venv/**' --glob '!node_modules/**' --glob '!.git/**' || true
```

### 0.2 Align identity / URLs

- [ ] `pyproject.toml` → `authors`, `project.urls.Homepage` match real GitHub
- [x] `examples/github-action/auditai-pr.yml` → `uses: iZenDeveloper/auditai@v0.1`
- [x] `README.md` Action example uses same `iZenDeveloper/auditai@v0.1`
- [ ] `LICENSE` copyright year/name OK

### 0.3 Version freeze

| File | Expected |
|------|----------|
| `pyproject.toml` | `version = "0.1.0"` |
| `src/auditai/__init__.py` | `__version__ = "0.1.0"` |
| `cloud/api/app/__init__.py` | `__version__ = "0.1.0"` |
| `cloud/dashboard/package.json` | `"version": "0.1.0"` |

- [ ] All four match `0.1.0`
- [ ] Add `CHANGELOG.md` section `[0.1.0] - YYYY-MM-DD` (see template §8)

### 0.4 Tests (must be green)

```bash
# CLI package
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,pdf]"
pytest -q
# expect: 16 passed

# Cloud API
cd cloud/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
# expect: 4 passed
cd ../..

# Dashboard build
cd cloud/dashboard
npm ci || npm install
npm run build
cd ../..

# Optional: Action script smoke (mock)
python examples/rag_demo/mock_server.py &
export AUDITAI_CONFIG=examples/rag_demo/auditai.yml
export AUDITAI_OUT=/tmp/auditai-out-release
export GITHUB_OUTPUT=/tmp/gha-out
bash action/run.sh
# expect: exit-code=1 (demo includes hallucinate case) in GITHUB_OUTPUT
```

- [ ] CLI tests pass  
- [ ] API tests pass  
- [ ] `npm run build` succeeds  
- [ ] Action script produces report files  

### 0.5 Manual product smoke

```bash
source .venv/bin/activate
auditai --version          # 0.1.0
auditai init --force       # or use examples/rag_demo
# with mock:
python examples/rag_demo/mock_server.py &
auditai run --config examples/rag_demo/auditai.yml
auditai report --pdf \
  --from examples/rag_demo/auditai-out/auditai-report.json \
  --out /tmp/compliance-v0.1.pdf \
  --project-name release-smoke
file /tmp/compliance-v0.1.pdf   # PDF document
```

- [ ] CLI run + PDF smoke OK  

---

## 1. First commit + GitHub repo

```bash
cd /path/to/auditai
git init -b main
git add .
git status   # review: no .venv, no node_modules, no *.db, no .env

git commit -m "chore: initial release v0.1.0

Open-core CLI, GitHub Action, cloud API stub, dashboard, compliance PDF."
```

- [ ] Initial commit created  

```bash
# Create empty public repo on GitHub first (no README), then:
git remote add origin GIT_REMOTE
git push -u origin main
```

- [ ] `main` pushed to GitHub  
- [ ] Repo is **public** (required for free Action consumers / simple install)  
- [ ] GitHub → Settings → Actions → General → allow Actions  

### 1.1 Repo polish (same day)

- [ ] Description: `Developer-first LLM/RAG safety audits for CI/CD`
- [ ] Topics: `llm`, `rag`, `ci-cd`, `github-actions`, `evaluation`, `openai`
- [ ] Enable Issues  
- [ ] Optional: Discussions  

---

## 2. Tag `v0.1.0` + moving major tag `v0.1`

GitHub Actions consumers often pin `@v0.1` (floating patch) or `@v0.1.0` (immutable).

```bash
git tag -a v0.1.0 -m "AuditAI v0.1.0 — first public release"
git push origin v0.1.0

# floating minor tag for Action users
git tag -f v0.1 v0.1.0
git push -f origin v0.1
```

- [ ] `v0.1.0` pushed  
- [ ] `v0.1` points at same commit  

---

## 3. GitHub Release notes

GitHub → Releases → **Draft a new release** → choose tag `v0.1.0`.

### Title
`v0.1.0 — Developer-first AI safety CI/CD`

### Body (copy-paste)

```markdown
## AuditAI v0.1.0

First public open-core release: audit RAG/LLM quality and basic prompt-injection safety inside CI.

### Install

```bash
pip install git+https://github.com/iZenDeveloper/auditai.git@v0.1.0
# PDF certificates:
pip install "auditai[pdf] @ git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
```

### GitHub Action

```yaml
- uses: iZenDeveloper/auditai@v0.1
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  with:
    config: auditai.yml
    comment-on-pr: "true"
```

### Highlights

- CLI: `auditai run` · YAML config · exit codes for gates (0/1/2/3)
- Metrics: Faithfulness · Answer Relevancy · Prompt Injection (BYOK OpenAI or mock)
- GitHub Action: PR comment + artifacts + fail job on threshold breach
- Cloud stub (optional): run history API + Next.js dashboard
- Compliance PDF (technical certificate + legal disclaimer)

### Not in v0.1

- PyPI package name reservation (optional follow-up)
- Multi-user cloud auth / billing
- Anthropic judge
- Marketplace Action listing (can publish after tag)

### Smoke

See repo `examples/rag_demo/` (mock server + intentional hallucination case → exit 1).
```

- [ ] Release published (not draft)  

---

## 4. Install verification (from clean machine / new venv)

```bash
python -m venv /tmp/auditai-verify && source /tmp/auditai-verify/bin/activate
pip install "git+https://github.com/iZenDeveloper/auditai.git@v0.1.0"
auditai --version
# 0.1.0

# Action ref check (needs gh + public repo)
gh api repos/iZenDeveloper/auditai/git/refs/tags/v0.1.0 --jq .object.sha
```

- [ ] Fresh `pip install` from tag works  
- [ ] `auditai --version` prints `0.1.0`  

### 4.1 Consumer Action dry-run (recommended)

In a throwaway fork or private test repo:

```yaml
# .github/workflows/auditai.yml
name: AuditAI
on: [pull_request]
permissions:
  contents: read
  pull-requests: write
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # copy examples/rag_demo or your real config
      - uses: iZenDeveloper/auditai@v0.1
        with:
          install: git+https://github.com/iZenDeveloper/auditai.git@v0.1.0
          config: auditai.yml
          working-directory: .
          comment-on-pr: "true"
```

- [ ] Workflow runs on a PR  
- [ ] Comment appears / artifact uploaded  
- [ ] Job fails when metrics fail (gate works)  

---

## 5. Optional: PyPI (do only if name is free)

```bash
# Check name availability
pip index versions auditai 2>&1 | head || curl -s https://pypi.org/pypi/auditai/json | head

# Build
source .venv/bin/activate
pip install build twine
python -m build
twine check dist/*

# TestPyPI first
twine upload --repository testpypi dist/*
# pip install -i https://test.pypi.org/simple/ auditai==0.1.0

# Production PyPI
twine upload dist/*
```

- [ ] Name available or rename package (`auditai-cli`, etc.)  
- [ ] TestPyPI OK  
- [ ] (Optional for v0.1) Production PyPI uploaded  
- [ ] If skipped: document git install as primary path in README  

**Note:** Name `auditai` may already be taken on PyPI. If so, publish as `auditai-cli` and update `name` + README in a patch `v0.1.1`.

---

## 6. Optional: GitHub Marketplace Action listing

After tag exists:

1. [ ] Ensure `action.yml` has `name`, `description`, `branding` (already set)
2. [ ] GitHub repo → **Release** `v0.1.0` includes Action  
3. [ ] Follow [Publishing actions in GitHub Marketplace](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace)
4. [ ] Categories: continuous-integration / code-quality  
5. [ ] Listing approved (can lag 1–2 days)

Marketplace is **optional** for v0.1 — `uses: iZenDeveloper/auditai@v0.1` works without it.

---

## 7. Cloud (optional for v0.1 public story)

v0.1 can ship **CLI + Action only**. Cloud is demo/premium hinge.

If you deploy cloud with this release:

- [ ] Deploy API (Fly/Render/Railway) with:
  - `AUDITAI_CLOUD_ALLOW_PUBLIC_PROJECT_CREATE=false`
  - `AUDITAI_CLOUD_ADMIN_TOKEN=<strong random>`
  - Postgres or durable volume for SQLite
- [ ] Deploy dashboard with `NEXT_PUBLIC_AUDITAI_API_URL=https://api.yourdomain`
- [ ] CORS limited to dashboard origin
- [ ] Document public URL in README “Cloud (beta)”
- [ ] Do **not** promise SLA / compliance legal stamp

If not deploying:

- [ ] README labels cloud as “self-host stub” only  

---

## 8. CHANGELOG template

Create `CHANGELOG.md`:

```markdown
# Changelog

## [0.1.0] - YYYY-MM-DD

### Added
- CLI: `auditai run|validate|init|report --pdf`
- YAML config v0.1, JSON/Markdown reports, CI exit codes
- Metrics: faithfulness, answer_relevancy, prompt_injection (BYOK OpenAI / mock)
- GitHub composite Action with PR comments + artifacts
- Cloud API stub (projects, runs ingest, compliance PDF)
- Next.js dashboard (history, sparklines, PDF download)
- Examples: rag_demo, GitHub/GitLab workflow samples

### Known limitations
- Judge provider: OpenAI + mock only
- Cloud: SQLite, no multi-user auth / billing
- DeepEval optional and not required path
- Compliance PDF is technical evidence only (see disclaimer)
```

- [ ] `CHANGELOG.md` committed (amend or follow-up commit before tag if needed)  

---

## 9. Post-release (same day)

### 9.1 Announcement kit (no ads)

- [ ] Short post: LinkedIn / X / Facebook group MLOps VN / Discord AI VN  
- [ ] One GIF or screenshot: PR comment table + fail gate  
- [ ] Link: Release + `examples/rag_demo`  

### 9.2 Growth-hack readiness

- [ ] Template PR body saved (from PRD)  
- [ ] List first **10** public RAG repos (not 50 yet)  
- [ ] Only open PRs after install path is verified (§4)  

### 9.3 Watch for 48h

- [ ] GitHub Issues enabled + watch notifications  
- [ ] Action failures from early adopters triaged  
- [ ] Hotfix → `v0.1.1` tag (don’t rewrite `v0.1.0` artifacts if PyPI published)  

---

## 10. Definition of Done — v0.1.0

Release is **done** when all of these are true:

| # | Criterion |
|---|-----------|
| 1 | `main` on GitHub, public |
| 2 | Annotated tag `v0.1.0` (+ optional floating `v0.1`) |
| 3 | GitHub Release notes published |
| 4 | Clean venv: `pip install git+…@v0.1.0` → `auditai --version` |
| 5 | At least one successful Action run against the tagged ref |
| 6 | README install + Action snippet use real `iZenDeveloper/auditai` |
| 7 | No known secret in git history |

**Not required for v0.1 Done:** PyPI, Marketplace badge, production cloud, 1000 stars.

---

## 11. Rollback

| Situation | Action |
|-----------|--------|
| Broken Action on `v0.1` floating tag | Move `v0.1` to last good commit: `git tag -f v0.1 <sha> && git push -f origin v0.1` |
| Broken `v0.1.0` immutable tag | Publish `v0.1.1`; never delete PyPI release |
| Secret leaked | Rotate keys; `git filter-repo` / BFG; force-push only if repo still private / zero adopters |

---

## 12. Suggested timebox

| Block | Duration |
|-------|----------|
| §0 Pre-flight + tests | 45–90 min |
| §1 Commit + push | 20 min |
| §2–3 Tag + Release | 20 min |
| §4 Verify install + Action | 30–60 min |
| §5 PyPI (optional) | 30–60 min |
| §9 Announce | 30 min |
| **Total** | **~3–5 hours** (without PyPI/cloud deploy) |

---

## Quick command card

```bash
# after iZenDeveloper/auditai fixed in docs:
pytest -q && (cd cloud/api && pytest -q)
git add . && git commit -m "chore: initial release v0.1.0"
git remote add origin git@github.com:iZenDeveloper/auditai.git
git push -u origin main
git tag -a v0.1.0 -m "v0.1.0"
git tag -f v0.1 v0.1.0
git push origin v0.1.0 v0.1
# then publish GitHub Release UI + verify pip install from tag
```
