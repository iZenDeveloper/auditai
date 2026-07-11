"""Compliance / AI safety audit certificate PDF generator.

Produces a technical certificate from audit run metrics.
This is NOT a government licence or legal opinion — see disclaimer in PDF.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Callable


@dataclass
class MetricLine:
    name: str
    mean: float | None
    threshold: float | None = None
    passed: bool | None = None
    n_scored: int | None = None


@dataclass
class CertificateData:
    project_name: str
    run_id: str
    overall_passed: bool
    exit_reason: str
    issued_at: datetime
    metrics: list[MetricLine] = field(default_factory=list)
    total_cases: int = 0
    failed_cases: int = 0
    judge_calls: int = 0
    client_run_id: str | None = None
    git_sha: str | None = None
    git_ref: str | None = None
    repo: str | None = None
    client_version: str | None = None
    top_failures: list[dict[str, Any]] = field(default_factory=list)
    issuer: str = "AuditAI"
    standard_refs: list[str] = field(
        default_factory=lambda: [
            "Technical self-assessment for common LLM/RAG safety checks",
            "Metrics: Faithfulness, Answer Relevancy, Prompt Injection resistance",
            "VN AI governance: supporting evidence only (not a government licence)",
        ]
    )


def certificate_from_report_json(
    data: dict[str, Any],
    *,
    project_name: str = "local-project",
) -> CertificateData:
    """Build certificate payload from CLI auditai-report.json shape."""
    aggregates = data.get("aggregates") or data.get("metric_aggregates") or {}
    metrics: list[MetricLine] = []
    for name, agg in aggregates.items():
        if not isinstance(agg, dict):
            continue
        metrics.append(
            MetricLine(
                name=name,
                mean=_f(agg.get("mean")),
                threshold=_f(agg.get("threshold")),
                passed=agg.get("passed"),
                n_scored=agg.get("n_scored"),
            )
        )

    issued = data.get("finished_at") or data.get("started_at")
    if isinstance(issued, str):
        try:
            issued_at = datetime.fromisoformat(issued.replace("Z", "+00:00"))
        except ValueError:
            issued_at = datetime.now(timezone.utc)
    else:
        issued_at = datetime.now(timezone.utc)

    meta = data.get("metadata") or {}
    return CertificateData(
        project_name=project_name,
        run_id=str(data.get("run_id") or data.get("id") or "unknown"),
        overall_passed=bool(data.get("overall_passed")),
        exit_reason=str(data.get("exit_reason") or ""),
        issued_at=issued_at if issued_at.tzinfo else issued_at.replace(tzinfo=timezone.utc),
        metrics=metrics,
        total_cases=int(data.get("total_cases") or 0),
        failed_cases=int(data.get("failed_cases") or 0),
        judge_calls=int(data.get("judge_calls") or 0),
        client_run_id=data.get("client_run_id") or data.get("run_id"),
        git_sha=meta.get("git_sha") or data.get("git_sha"),
        git_ref=meta.get("git_ref") or data.get("git_ref"),
        repo=meta.get("repo") or data.get("repo"),
        client_version=data.get("client_version"),
        top_failures=list(data.get("top_failures") or [])[:5],
    )


def build_compliance_pdf(cert: CertificateData) -> bytes:
    """Return PDF bytes for a compliance certificate."""
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
    except ImportError as e:
        raise RuntimeError(
            "PDF support requires fpdf2. Install with: pip install 'auditai[pdf]' or pip install fpdf2"
        ) from e

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(16, 16, 16)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    font_path, bold_path = _dejavu_paths()
    if font_path:
        pdf.add_font("DejaVu", "", str(font_path))
        if bold_path and bold_path.exists():
            pdf.add_font("DejaVu", "B", str(bold_path))
            has_bold = True
        else:
            has_bold = False
        family = "DejaVu"
    else:
        family = "Helvetica"
        has_bold = True

    def sf(style: str = "", size: int = 10) -> None:
        if style == "B" and family == "DejaVu" and not has_bold:
            style = ""
        if style == "B" and family == "Helvetica":
            style = "B"
        pdf.set_font(family, style, size)

    def line(text: str, size: int = 10, style: str = "", gap: float = 6) -> None:
        sf(style, size)
        pdf.set_x(pdf.l_margin)
        # usable width
        w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.multi_cell(w, gap, _safe(text, family), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Header band
    pdf.set_fill_color(26, 34, 44)
    pdf.rect(0, 0, 210, 34, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(16, 10)
    sf("B", 15)
    pdf.cell(0, 8, _safe("AuditAI - AI Safety Audit Certificate", family), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(16)
    sf("", 9)
    pdf.cell(
        0,
        6,
        _safe("Giay chung nhan Kiem thu An toan AI (ban ky thuat)", family),
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_text_color(30, 30, 30)
    pdf.ln(10)

    if cert.overall_passed:
        pdf.set_fill_color(220, 252, 231)
        pdf.set_text_color(22, 101, 52)
        verdict = "VERDICT: PASSED"
    else:
        pdf.set_fill_color(254, 226, 226)
        pdf.set_text_color(153, 27, 27)
        verdict = "VERDICT: FAILED"

    sf("B", 13)
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_x(pdf.l_margin)
    pdf.cell(w, 10, verdict, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(3)

    line(f"Project / Du an: {cert.project_name}", style="B")
    line(f"Certificate ID: {cert.run_id}")
    if cert.client_run_id and cert.client_run_id != cert.run_id:
        line(f"Client run ID: {cert.client_run_id}")
    line(
        "Issued at (UTC): "
        + cert.issued_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    line(f"Exit reason: {cert.exit_reason or '-'}")
    line(
        f"Cases: {cert.total_cases} total / {cert.failed_cases} target errors / {cert.judge_calls} judge calls"
    )
    if cert.repo:
        line(f"Repository: {cert.repo}")
    if cert.git_sha:
        line(f"Git SHA: {str(cert.git_sha)[:40]}")
    if cert.git_ref:
        line(f"Git ref: {cert.git_ref}")
    if cert.client_version:
        line(f"CLI version: {cert.client_version}")

    pdf.ln(2)
    line("Metrics / Chi so", size=12, style="B", gap=7)

    # Metrics as text rows (more robust than nested cells)
    if not cert.metrics:
        line("No metrics recorded")
    else:
        for m in cert.metrics:
            passed = "YES" if m.passed else ("NO" if m.passed is False else "-")
            line(
                f"- {m.name}: mean={_fmt(m.mean)}  threshold={_fmt(m.threshold)}  "
                f"pass={passed}  n={m.n_scored if m.n_scored is not None else '-'}"
            )

    if cert.top_failures:
        pdf.ln(1)
        line("Top failures (summary)", size=12, style="B", gap=7)
        for i, f in enumerate(cert.top_failures[:5], start=1):
            case_id = str(f.get("case_id") or f.get("id") or "?")
            metric = str(f.get("metric") or "")
            score = f.get("score")
            score_s = _fmt(float(score)) if score is not None else "-"
            q = str(f.get("question") or "")[:90]
            line(f"{i}. [{case_id}] {metric}={score_s}  {q}")

    pdf.ln(1)
    line("Scope & references", size=12, style="B", gap=7)
    for ref in cert.standard_refs:
        line(f"* {ref}")

    pdf.ln(1)
    line("Disclaimer / Tuyen bo mien tru", size=11, style="B", gap=6)
    pdf.set_text_color(80, 80, 80)
    line(
        "This document is an automated technical audit report generated by AuditAI from "
        "customer-configured tests (BYOK LLM-as-judge). It is supporting evidence for "
        "internal quality and risk processes only. It is NOT a government licence, NOT a "
        "legal certification under Vietnamese AI regulations, and NOT legal advice. "
        "Organizations remain responsible for compliance, data protection, and model risk. "
        "Tai lieu nay la bao cao kiem thu ky thuat tu dong; khong phai giay phep nha nuoc "
        "va khong thay the y kien phap ly.",
        size=8,
        gap=4,
    )
    pdf.set_text_color(30, 30, 30)

    pdf.ln(4)
    line(f"Generated by {cert.issuer}")
    line(f"Document hash seed: {cert.run_id}")

    pdf.set_y(-18)
    sf("", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(pdf.l_margin)
    pdf.cell(
        w,
        5,
        _safe("auditai - open-core AI safety CI/CD - confidential to recipient", family),
        align="C",
    )

    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


def write_compliance_pdf(cert: CertificateData, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_compliance_pdf(cert))
    return path


def _fmt(n: float | None) -> str:
    if n is None:
        return "-"
    return f"{n:.3f}"


def _f(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe(text: str, family: str) -> str:
    if family != "Helvetica":
        return text
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _dejavu_paths() -> tuple[Path | None, Path | None]:
    here = Path(__file__).resolve().parent
    bundled = here / "fonts" / "DejaVuSans.ttf"
    bundled_bold = here / "fonts" / "DejaVuSans-Bold.ttf"
    system_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    ]
    regular: Path | None = bundled if bundled.exists() else None
    bold: Path | None = bundled_bold if bundled_bold.exists() else None
    if regular is None:
        for c in system_candidates:
            if c.exists():
                regular = c
                break
    if bold is None and regular is not None:
        cand = regular.with_name("DejaVuSans-Bold.ttf")
        if cand.exists():
            bold = cand
    return regular, bold
