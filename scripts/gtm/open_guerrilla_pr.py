#!/usr/bin/env python3
"""One-shot guerrilla pipeline: prep → audit → PR body → fork/push → open PR → log.

Usage:
  export GITHUB_TOKEN=ghp_...          # or ~/.config/github_token
  export XAI_API_KEY=...               # if --judge xai
  # optional: OPENAI_API_KEY for --judge openai

  python scripts/gtm/open_guerrilla_pr.py --repo owner/name
  python scripts/gtm/open_guerrilla_pr.py --repo owner/name --judge xai --model grok-4.3
  python scripts/gtm/open_guerrilla_pr.py --repo owner/name --dry-run   # no push/PR

Ethics: public repos only, 2–3 quality PRs/day, no spam.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKDIR = Path("/tmp/auditai-guerrilla")
DEFAULT_OUT = ROOT / "docs" / "gtm" / "out"
DEFAULT_TEMPLATE = ROOT / "docs" / "gtm" / "templates" / "PR_BODY_VI.md"
PR_LOG = DEFAULT_OUT / "pr_log.jsonl"
ADAPTER_PORT = 18080


class StepError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(msg, flush=True)


def _redact(s: str) -> str:
    """Strip secrets from log lines (tokens embedded in git remote URLs, etc.)."""
    s = re.sub(r"x-access-token:[^@\s]+@", "x-access-token:***@", s)
    s = re.sub(r"ghp_[A-Za-z0-9]{20,}", "ghp_***", s)
    s = re.sub(r"github_pat_[A-Za-z0-9_]{20,}", "github_pat_***", s)
    s = re.sub(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9._-]+\b", "eyJ***", s)
    return s


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    log("+ " + _redact(" ".join(cmd)))
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged,
        check=check,
        text=True,
        capture_output=capture,
    )


def load_secret_file(*candidates: Path) -> str:
    for p in candidates:
        if p.is_file():
            return p.read_text(encoding="utf-8").strip().replace("\n", "").replace("\r", "")
    return ""


def ensure_github_token() -> str:
    tok = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if not tok:
        tok = load_secret_file(
            Path.home() / ".config" / "github_token",
            Path.home() / ".config" / "gh_token",
        )
    if not tok:
        raise StepError(
            "GITHUB_TOKEN missing. Export it or write ~/.config/github_token (chmod 600)."
        )
    os.environ["GITHUB_TOKEN"] = tok
    os.environ["GH_TOKEN"] = tok
    return tok


def ensure_judge_key(provider: str) -> None:
    if provider == "mock":
        return
    if provider == "xai":
        if os.environ.get("XAI_API_KEY"):
            return
        # Prefer console API key file; fall back to Grok CLI OIDC access token
        key = load_secret_file(
            Path.home() / ".config" / "xai_api_key",
            Path.home() / ".config" / "xai_token",
        )
        if not key:
            auth = Path.home() / ".grok" / "auth.json"
            if auth.is_file():
                try:
                    data = json.loads(auth.read_text(encoding="utf-8"))
                    entry = next(iter(data.values()))
                    key = (entry.get("key") or entry.get("access_token") or "").strip()
                except Exception:
                    key = ""
        if not key:
            raise StepError(
                "XAI_API_KEY missing. Export it, write ~/.config/xai_api_key, "
                "or login Grok CLI (~/.grok/auth.json)."
            )
        os.environ["XAI_API_KEY"] = key
        return
    if provider == "openai":
        if os.environ.get("OPENAI_API_KEY"):
            return
        key = load_secret_file(Path.home() / ".config" / "openai_api_key")
        if not key:
            raise StepError("OPENAI_API_KEY missing for --judge openai.")
        os.environ["OPENAI_API_KEY"] = key


def find_auditai() -> list[str]:
    """Return argv prefix to invoke auditai CLI."""
    venv = ROOT / ".venv" / "bin" / "auditai"
    if venv.is_file():
        return [str(venv)]
    which = shutil.which("auditai")
    if which:
        return [which]
    return [sys.executable, "-m", "auditai"]


def repo_slug(repo: str) -> tuple[str, str]:
    if "/" not in repo or repo.count("/") != 1:
        raise StepError("--repo must be owner/name")
    owner, name = repo.split("/", 1)
    if not owner or not name:
        raise StepError("invalid --repo")
    return owner, name


def dest_dir(workdir: Path, repo: str) -> Path:
    owner, name = repo_slug(repo)
    return workdir / f"{owner}_{name}"


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def kill_port(port: int) -> None:
    try:
        out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return
    for pid in out.split():
        try:
            os.kill(int(pid), signal.SIGKILL)
        except (ProcessLookupError, ValueError):
            pass


def patch_judge_yml(yml_path: Path, provider: str, model: str | None) -> None:
    """Set judge.provider / judge.model inside the top-level judge: block only."""
    lines = yml_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_judge = False
    provider_set = model_set = False
    for line in lines:
        if re.match(r"^judge:\s*$", line):
            in_judge = True
            out.append(line)
            continue
        if in_judge and re.match(r"^[^\s#]", line):
            in_judge = False
        if in_judge and not line.lstrip().startswith("#"):
            if re.match(r"^\s*provider:\s*", line):
                out.append(f"  provider: {provider}")
                provider_set = True
                continue
            if re.match(r"^\s*model:\s*", line):
                if model:
                    out.append(f'  model: "{model}"')
                    model_set = True
                else:
                    out.append(line)
                continue
        out.append(line)

    if not provider_set:
        out.extend(["", "judge:", f"  provider: {provider}"])
        if model:
            out.append(f'  model: "{model}"')
            model_set = True
    elif model and not model_set:
        fixed: list[str] = []
        for line in out:
            fixed.append(line)
            if re.match(r"^\s*provider:\s*" + re.escape(provider) + r"\s*$", line):
                fixed.append(f'  model: "{model}"')
                model_set = True
        out = fixed

    yml_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def prepare_yml_for_commit(yml_path: Path) -> None:
    """Reset committed config to safe defaults (mock judge + env-based target URL).

    Local audit may use xai/openai, but the PR must not hard-default external APIs.
    """
    text = yml_path.read_text(encoding="utf-8")
    # target URL → env override
    text = re.sub(
        r'(?m)^(\s*url:\s*)"[^"]*"',
        r'\1"${AUDITAI_TARGET_URL:-http://127.0.0.1:18080/chat}"',
        text,
        count=1,
    )
    yml_path.write_text(text, encoding="utf-8")
    patch_judge_yml(yml_path, "mock", "mock")


def default_model(provider: str) -> str:
    if provider == "xai":
        return "grok-4.3"
    if provider == "openai":
        return "gpt-4o-mini"
    return "mock"


def start_adapter(clone: Path) -> subprocess.Popen[str]:
    adapter = clone / "tests" / "auditai" / "mock_adapter.py"
    if not adapter.is_file():
        raise StepError(f"missing adapter: {adapter}")
    kill_port(ADAPTER_PORT)
    if not port_free(ADAPTER_PORT):
        raise StepError(f"port {ADAPTER_PORT} still busy")
    proc = subprocess.Popen(
        [sys.executable, str(adapter)],
        cwd=str(clone),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    for _ in range(30):
        time.sleep(0.1)
        if not port_free(ADAPTER_PORT):
            return proc
        if proc.poll() is not None:
            raise StepError("mock_adapter exited early")
    raise StepError("mock_adapter failed to bind :18080")


def gh_api_user() -> str:
    cp = run(["gh", "api", "user", "--jq", ".login"], capture=True)
    login = (cp.stdout or "").strip()
    if not login:
        raise StepError("gh api user failed — check token scopes")
    return login


def ensure_fork(upstream: str, fork_owner: str, name: str) -> str:
    """Return fork full_name owner/name. Creates fork if missing."""
    fork = f"{fork_owner}/{name}"
    view = run(
        ["gh", "repo", "view", fork, "--json", "name"],
        check=False,
        capture=True,
    )
    if view.returncode == 0:
        return fork
    log(f"== fork {upstream} → {fork_owner} ==")
    run(["gh", "repo", "fork", upstream, "--default-branch-only"], check=True)
    # wait for availability
    for _ in range(20):
        time.sleep(1)
        if run(["gh", "repo", "view", fork, "--json", "name"], check=False, capture=True).returncode == 0:
            return fork
    raise StepError(f"fork not visible yet: {fork}")


def git_https_public(url_or_slug: str) -> str:
    """Public HTTPS remote (no token in URL — auth via GH_TOKEN/gh/git credential)."""
    if url_or_slug.startswith("https://github.com/"):
        path = url_or_slug.removeprefix("https://github.com/").removesuffix(".git")
    elif "/" in url_or_slug and not url_or_slug.startswith("git@"):
        path = url_or_slug
    else:
        path = url_or_slug
    return f"https://github.com/{path}.git"


def configure_git_auth(token: str) -> None:
    """Prefer gh as git credential helper so remotes never embed PATs."""
    if shutil.which("gh"):
        run(["gh", "auth", "setup-git"], check=False, capture=True)
    # Fallback env for git/https (not logged)
    os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")
    # Some git builds honor this when using https://github.com/ without helper
    os.environ["GH_TOKEN"] = token
    os.environ["GITHUB_TOKEN"] = token


def select_commit_files(clone: Path, workflow_example_only: bool) -> list[Path]:
    base = clone / "tests" / "auditai"
    files = [
        base / "auditai.yml",
        base / "dataset.json",
        base / "mock_adapter.py",
        base / "README.md",
    ]
    # optional sample report
    sample = base / "sample-report.md"
    report_md = base / "auditai-out" / "auditai-report.md"
    if report_md.is_file():
        sample.write_text(
            "> Sample local AuditAI run. Re-run for fresh numbers.\n\n"
            + report_md.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        files.append(sample)
    elif sample.is_file():
        files.append(sample)

    example = base / "workflow-auditai.yml.example"
    wf = clone / ".github" / "workflows" / "auditai.yml"
    if workflow_example_only:
        if wf.is_file() and not example.is_file():
            example.write_text(wf.read_text(encoding="utf-8"), encoding="utf-8")
        if example.is_file():
            files.append(example)
        # do not commit .github/workflows/auditai.yml (needs PAT workflow scope)
    else:
        if wf.is_file():
            files.append(wf)
        if example.is_file():
            files.append(example)

    # prefer README over README_GUERRILLA
    guerrilla = base / "README_GUERRILLA.md"
    if guerrilla.is_file() and not (base / "README.md").is_file():
        files.append(guerrilla)

    existing = [p for p in files if p.is_file()]
    if not existing:
        raise StepError("no files to commit under tests/auditai")
    return existing


def append_pr_log(entry: dict) -> None:
    PR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PR_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="One-shot guerrilla AuditAI PR")
    ap.add_argument("--repo", required=True, help="upstream owner/name")
    ap.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    ap.add_argument("--questions", type=int, default=20)
    ap.add_argument("--judge", choices=["mock", "xai", "openai"], default="mock")
    ap.add_argument("--model", default=None, help="judge model (default by provider)")
    ap.add_argument("--branch", default="ci/auditai-quality-gate")
    ap.add_argument("--title", default="ci: add optional AuditAI RAG quality smoke suite")
    ap.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="PR body template",
    )
    ap.add_argument(
        "--workflow-example-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="commit workflow as tests/auditai/*.example only (default: true)",
    )
    ap.add_argument("--skip-prep", action="store_true", help="reuse existing clone scaffold")
    ap.add_argument("--skip-audit", action="store_true", help="reuse existing auditai-out report")
    ap.add_argument("--dry-run", action="store_true", help="prep+audit+body only (no push/PR)")
    ap.add_argument("--yes", action="store_true", help="skip interactive confirm before PR")
    ap.add_argument(
        "--auditai-install",
        default="",
        help="unused placeholder for future remote install pin",
    )
    args = ap.parse_args()

    owner, name = repo_slug(args.repo)
    model = args.model or default_model(args.judge)
    token = ensure_github_token()
    ensure_judge_key(args.judge)

    # verify gh
    if shutil.which("gh") is None:
        raise StepError("`gh` CLI not found")
    me = gh_api_user()
    log(f"== github user: {me} ==")

    clone = dest_dir(args.workdir, args.repo)
    prep_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "gtm" / "guerrilla_prep.py"),
        "--repo",
        args.repo,
        "--workdir",
        str(args.workdir),
        "--questions",
        str(args.questions),
    ]
    if args.workflow_example_only:
        prep_cmd.append("--workflow-example-only")

    if not args.skip_prep:
        log(f"== prep {args.repo} ==")
        run(prep_cmd)
    elif not clone.is_dir():
        raise StepError(f"--skip-prep but missing clone: {clone}")

    yml = clone / "tests" / "auditai" / "auditai.yml"
    if not yml.is_file():
        raise StepError(f"missing {yml}")
    patch_judge_yml(yml, args.judge, model)

    report = clone / "tests" / "auditai" / "auditai-out" / "auditai-report.json"
    adapter_proc: subprocess.Popen[str] | None = None
    try:
        if not args.skip_audit:
            log(f"== audit judge={args.judge} model={model} ==")
            adapter_proc = start_adapter(clone)
            auditai = find_auditai()
            # allow non-zero exit when metrics fail — still produce report
            cp = run(
                [*auditai, "run", "--config", str(yml)],
                cwd=clone,
                check=False,
            )
            if not report.is_file():
                raise StepError(f"audit produced no report (exit={cp.returncode})")
            log(f"audit exit={cp.returncode} report={report}")
        elif not report.is_file():
            raise StepError(f"--skip-audit but missing report: {report}")

        pr_body = clone / "tests" / "auditai" / "pr_body.md"
        log("== fill PR body ==")
        run(
            [
                sys.executable,
                str(ROOT / "scripts" / "gtm" / "fill_pr_body.py"),
                "--report",
                str(report),
                "--template",
                str(args.template),
                "--out",
                str(pr_body),
            ]
        )

        # load summary for log
        report_data = json.loads(report.read_text(encoding="utf-8"))
        usage = report_data.get("judge_usage") or {}

        if args.dry_run:
            log("== dry-run: stop before fork/push/PR ==")
            log(f"clone:   {clone}")
            log(f"report:  {report}")
            log(f"pr_body: {pr_body}")
            append_pr_log(
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "repo": args.repo,
                    "dry_run": True,
                    "judge": args.judge,
                    "model": model,
                    "overall_passed": report_data.get("overall_passed"),
                    "judge_usage": usage,
                    "clone": str(clone),
                }
            )
            return 0

        # Never commit live judge keys/provider used for baseline (opt-in mock for PR)
        prepare_yml_for_commit(yml)

        if not args.yes:
            log(f"About to fork/push/open PR against {args.repo} as {me}")
            log("Pass --yes to skip this prompt in automation.")
            try:
                ans = input("Continue? [y/N] ").strip().lower()
            except EOFError:
                ans = "n"
            if ans not in {"y", "yes"}:
                log("aborted")
                return 2

        fork = ensure_fork(args.repo, me, name)
        configure_git_auth(token)
        log(f"== git branch {args.branch} ==")
        # remotes — never put PAT in the remote URL (leaks via logs / git config)
        run(["git", "remote", "remove", "fork"], cwd=clone, check=False, capture=True)
        run(
            ["git", "remote", "add", "fork", git_https_public(fork)],
            cwd=clone,
            check=False,
        )
        # ensure origin is upstream
        run(
            [
                "git",
                "remote",
                "set-url",
                "origin",
                git_https_public(args.repo),
            ],
            cwd=clone,
            check=False,
        )
        run(["git", "fetch", "origin", "main"], cwd=clone, check=False)
        run(
            ["git", "checkout", "-B", args.branch, "origin/main"],
            cwd=clone,
            check=False,
        )
        # if origin/main missing, use current HEAD
        run(["git", "checkout", "-B", args.branch], cwd=clone, check=False)

        files = select_commit_files(clone, args.workflow_example_only)
        run(["git", "add", "--"] + [str(p.relative_to(clone)) for p in files], cwd=clone)

        # commit if staged
        st = run(["git", "status", "--porcelain"], cwd=clone, capture=True)
        if not (st.stdout or "").strip():
            log("nothing to commit (already clean?)")
        else:
            run(
                [
                    "git",
                    "commit",
                    "-m",
                    "ci: add optional AuditAI RAG quality smoke suite\n\n"
                    "Scaffold dataset, mock adapter, and docs for optional "
                    "faithfulness / relevancy / prompt-injection checks via AuditAI.\n",
                ],
                cwd=clone,
            )

        log(f"== push fork:{args.branch} ==")
        push = run(
            ["git", "push", "-u", "fork", args.branch],
            cwd=clone,
            check=False,
            capture=True,
        )
        if push.returncode != 0:
            err = (push.stderr or "") + (push.stdout or "")
            if "workflow" in err.lower() and "scope" in err.lower():
                raise StepError(
                    "Push rejected: PAT lacks `workflow` scope. "
                    "Re-run with default --workflow-example-only "
                    "(or add workflow scope to the token)."
                )
            raise StepError(f"git push failed:\n{err}")

        log("== create PR ==")
        pr = run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                args.repo,
                "--head",
                f"{me}:{args.branch}",
                "--base",
                "main",
                "--title",
                args.title,
                "--body-file",
                str(pr_body),
            ],
            capture=True,
            check=False,
        )
        pr_url = (pr.stdout or "").strip()
        if pr.returncode != 0 or not pr_url.startswith("http"):
            # maybe already exists
            listed = run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--repo",
                    args.repo,
                    "--head",
                    f"{me}:{args.branch}",
                    "--json",
                    "url,number,state",
                ],
                capture=True,
                check=False,
            )
            try:
                arr = json.loads(listed.stdout or "[]")
                if arr:
                    pr_url = arr[0]["url"]
                    log(f"existing PR: {pr_url}")
                else:
                    raise StepError(f"gh pr create failed:\n{pr.stderr}\n{pr.stdout}")
            except json.JSONDecodeError as e:
                raise StepError(f"gh pr create failed:\n{pr.stderr}\n{pr.stdout}") from e
        else:
            log(f"PR: {pr_url}")

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "repo": args.repo,
            "fork": fork,
            "branch": args.branch,
            "pr_url": pr_url,
            "judge": args.judge,
            "model": model,
            "overall_passed": report_data.get("overall_passed"),
            "exit_reason": report_data.get("exit_reason"),
            "judge_calls": report_data.get("judge_calls"),
            "judge_usage": usage,
            "workflow_example_only": args.workflow_example_only,
            "author": me,
        }
        append_pr_log(entry)
        log(f"logged → {PR_LOG}")
        log("Done.")
        return 0
    finally:
        if adapter_proc and adapter_proc.poll() is None:
            adapter_proc.terminate()
            try:
                adapter_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                adapter_proc.kill()
        kill_port(ADAPTER_PORT)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StepError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    except subprocess.CalledProcessError as e:
        print(f"ERROR: command failed ({e.returncode}): {e.cmd}", file=sys.stderr)
        raise SystemExit(1) from e
