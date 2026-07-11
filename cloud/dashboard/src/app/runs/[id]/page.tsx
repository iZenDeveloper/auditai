"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { downloadCompliancePdf, fetchProject, fetchRun } from "@/lib/api";
import { clearApiKey, getApiKey } from "@/lib/auth";
import type { ProjectInfo, RunDetail } from "@/lib/types";

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [run, setRun] = useState<RunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pdfBusy, setPdfBusy] = useState(false);

  useEffect(() => {
    const key = getApiKey();
    if (!key) {
      router.replace("/");
      return;
    }
    void (async () => {
      try {
        const [p, r] = await Promise.all([
          fetchProject(key),
          fetchRun(key, params.id),
        ]);
        setProject(p);
        setRun(r);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load run");
      }
    })();
  }, [params.id, router]);

  return (
    <div className="min-h-screen pb-16">
      <Header
        project={project}
        onSignOut={() => {
          clearApiKey();
          router.replace("/");
        }}
      />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <Link
          href="/"
          className="text-sm text-accent-soft hover:text-white"
        >
          ← Back to history
        </Link>

        {error && (
          <p className="mt-4 rounded-lg border border-fail/30 bg-fail/10 px-3 py-2 text-sm text-red-300">
            {error}
          </p>
        )}

        {!run && !error && (
          <p className="mt-8 text-ink-400">Loading run…</p>
        )}

        {run && (
          <article className="mt-6 space-y-6">
            <header className="rounded-2xl border border-ink-800 bg-ink-900/60 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p
                    className={`text-sm font-semibold ${
                      run.overall_passed ? "text-pass" : "text-fail"
                    }`}
                  >
                    {run.overall_passed ? "PASSED" : "FAILED"}
                  </p>
                  <h1 className="mt-1 font-mono text-lg text-white">
                    {run.id}
                  </h1>
                  <p className="mt-1 text-sm text-ink-400">{run.exit_reason}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <p className="text-xs text-ink-500">
                    {new Date(run.created_at).toLocaleString()}
                  </p>
                  <button
                    type="button"
                    disabled={pdfBusy}
                    onClick={async () => {
                      const key = getApiKey();
                      if (!key) return;
                      setPdfBusy(true);
                      setError(null);
                      try {
                        await downloadCompliancePdf(key, run.id);
                      } catch (err) {
                        setError(
                          err instanceof Error
                            ? err.message
                            : "PDF download failed"
                        );
                      } finally {
                        setPdfBusy(false);
                      }
                    }}
                    className="rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-white hover:bg-accent-dim disabled:opacity-50"
                  >
                    {pdfBusy ? "Generating…" : "Export compliance PDF"}
                  </button>
                </div>
              </div>

              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                <Stat label="Faithfulness" value={run.faithfulness_mean} />
                <Stat label="Relevancy" value={run.answer_relevancy_mean} />
                <Stat label="Injection" value={run.prompt_injection_mean} />
                <Stat
                  label="Cases"
                  value={run.total_cases}
                  raw
                />
              </dl>

              <div className="mt-4 flex flex-wrap gap-3 font-mono text-xs text-ink-400">
                {run.git_sha && <span>sha {run.git_sha.slice(0, 7)}</span>}
                {run.git_ref && <span>ref {run.git_ref}</span>}
                {run.repo && <span>repo {run.repo}</span>}
                {run.client_version && <span>cli v{run.client_version}</span>}
              </div>
            </header>

            {run.payload?.aggregates && (
              <section className="rounded-2xl border border-ink-800 bg-ink-900/50 p-5">
                <h2 className="text-sm font-medium uppercase tracking-wide text-ink-400">
                  Aggregates
                </h2>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="text-xs text-ink-500">
                      <tr>
                        <th className="py-2 pr-4">Metric</th>
                        <th className="py-2 pr-4">Mean</th>
                        <th className="py-2 pr-4">Threshold</th>
                        <th className="py-2">Pass</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-ink-800">
                      {Object.entries(run.payload.aggregates).map(
                        ([name, agg]) => (
                          <tr key={name}>
                            <td className="py-2 pr-4 font-mono text-ink-200">
                              {name}
                            </td>
                            <td className="py-2 pr-4 font-mono tabular-nums">
                              {agg.mean?.toFixed(3) ?? "—"}
                            </td>
                            <td className="py-2 pr-4 font-mono tabular-nums text-ink-400">
                              {agg.threshold?.toFixed(2) ?? "—"}
                            </td>
                            <td className="py-2">
                              {agg.passed == null
                                ? "—"
                                : agg.passed
                                  ? "✅"
                                  : "❌"}
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {run.payload?.top_failures && run.payload.top_failures.length > 0 && (
              <section className="rounded-2xl border border-ink-800 bg-ink-900/50 p-5">
                <h2 className="text-sm font-medium uppercase tracking-wide text-ink-400">
                  Top failures
                </h2>
                <ul className="mt-3 space-y-3">
                  {run.payload.top_failures.map((f, i) => (
                    <li
                      key={`${f.case_id}-${i}`}
                      className="rounded-xl border border-ink-800/80 bg-ink-950/50 p-3"
                    >
                      <p className="text-sm text-ink-100">
                        <span className="font-mono text-accent-soft">
                          {f.case_id}
                        </span>{" "}
                        <span className="text-ink-500">·</span>{" "}
                        <span className="font-mono text-xs text-ink-300">
                          {f.metric}={f.score.toFixed(2)}
                        </span>
                      </p>
                      {f.question && (
                        <p className="mt-1 text-sm text-ink-300">{f.question}</p>
                      )}
                      {f.reason && (
                        <p className="mt-1 text-xs text-ink-500">{f.reason}</p>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </article>
        )}
      </main>
    </div>
  );
}

function Stat({
  label,
  value,
  raw,
}: {
  label: string;
  value: number | null;
  raw?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs text-ink-500">{label}</dt>
      <dd className="font-mono text-lg tabular-nums text-white">
        {value == null ? "—" : raw ? value : value.toFixed(2)}
      </dd>
    </div>
  );
}
