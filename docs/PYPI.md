# Publish AuditAI to PyPI

**Package name:** `auditai` (verified free on pypi.org as of 2026-07-16)  
**Do not use:** `audit-ai` (different existing package).  
**Current version:** `0.1.1` (matches GitHub release tag `v0.1.1`).

---

## 0. Pre-flight (done locally)

```bash
cd /path/to/auditai
pytest -q
rm -rf dist && uv build   # or: python -m build
# smoke:
python -m venv /tmp/auditai-pypi-smoke && \
  /tmp/auditai-pypi-smoke/bin/pip install dist/auditai-*.whl && \
  /tmp/auditai-pypi-smoke/bin/auditai --version   # → 0.1.1
```

---

## 1. Choose auth path

### A) Trusted Publishing (recommended)

1. Create account: https://pypi.org/account/register/  
2. Enable 2FA.  
3. **Publishing → Pending publisher** (or project settings after first upload):  
   - PyPI project name: `auditai`  
   - Owner: `iZenDeveloper`  
   - Repository: `auditai`  
   - Workflow name: `publish-pypi.yml`  
   - Environment name: `pypi`  
4. On GitHub: **Settings → Environments → New environment `pypi`** (empty OK).  
5. Trigger:

```bash
# Option 1 — manual
gh workflow run publish-pypi.yml

# Option 2 — re-push existing tag (only if needed)
git push origin v0.1.1 --force   # avoid force if tag already good; use workflow_dispatch instead
```

### B) API token (fast first upload)

1. PyPI → Account settings → API tokens → **Entire account** (first publish) or scope to `auditai` after.  
2. Local:

```bash
# never commit this file
mkdir -p ~/.config
# paste token only (pypi-AgEIcHlwaS5vcmc...)
printf '%s' 'pypi-...' > ~/.config/pypi_token
chmod 600 ~/.config/pypi_token

./scripts/publish_pypi.sh
# or:
uv publish --token "$(cat ~/.config/pypi_token)"
```

3. Or GitHub secret `PYPI_API_TOKEN` and uncomment `password:` in `.github/workflows/publish-pypi.yml`.

---

## 2. After first successful upload

```bash
pip index versions auditai
pip install auditai
auditai --version
```

Update guerrilla PR bodies / STATUS to lead with:

```bash
pip install auditai
# optional: pip install "auditai[pdf]"
```

Badges (README):

```markdown
[![PyPI](https://img.shields.io/pypi/v/auditai)](https://pypi.org/project/auditai/)
[![PyPI downloads](https://img.shields.io/pypi/dm/auditai)](https://pypi.org/project/auditai/)
```

---

## 3. Later releases

1. Bump `version` in `pyproject.toml` + `src/auditai/__init__.py`  
2. `CHANGELOG.md` section  
3. Commit → tag `vX.Y.Z` → push tag → workflow publishes  
4. GitHub Release notes from CHANGELOG  

---

## 4. Troubleshooting

| Symptom | Fix |
|---------|-----|
| 403 Invalid token | Token scope; 2FA; use `__token__` user with twine |
| 400 File already exists | Bump version or `skip-existing` |
| OIDC failed | Trusted publisher fields must match workflow filename + env `pypi` |
| Name taken | Unlikely for `auditai`; verify https://pypi.org/project/auditai/ |
