"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchProject, fetchRuns } from "@/lib/api";
import { clearApiKey, getApiKey } from "@/lib/auth";
import type { ProjectInfo, RunSummary } from "@/lib/types";
import { Header } from "./Header";
import { LoginForm } from "./LoginForm";
import { MetricCard } from "./MetricCard";
import { RunsTable } from "./RunsTable";

export function Dashboard() {
  const [ready, setReady] = useState(false);
  const [apiKey, setKeyState] = useState<string | null>(null);
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (key: string) => {
    setLoading(true);
    setError(null);
    try {
      const [p, r] = await Promise.all([fetchProject(key), fetchRuns(key, 50)]);
      setProject(p);
      // API returns newest first; keep that for table
      setRuns(r);
      setKeyState(key);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
      clearApiKey();
      setKeyState(null);
      setProject(null);
      setRuns([]);
    } finally {
      setLoading(false);
      setReady(true);
    }
  }, []);

  useEffect(() => {
    const key = getApiKey();
    if (key) {
      void load(key);
    } else {
      setReady(true);
    }
  }, [load]);

  // chronological for sparklines (oldest → newest)
  const chronological = useMemo(() => [...runs].reverse(), [runs]);

  const series = useMemo(
    () => ({
      faithfulness: chronological.map((r) => r.faithfulness_mean),
      relevancy: chronological.map((r) => r.answer_relevancy_mean),
      injection: chronological.map((r) => r.prompt_injection_mean),
    }),
    [chronological]
  );

  const latest = runs[0] ?? null;
  const passRate =
    runs.length === 0
      ? null
      : runs.filter((r) => r.overall_passed).length / runs.length;

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center text-ink-400">
        Loading…
      </div>
    );
  }

  if (!apiKey || !project) {
    return (
      <div className="min-h-screen">
        <Header />
        <main className="mx-auto flex max-w-6xl flex-col items-center px-4 py-16">
          <LoginForm onSuccess={() => {
            const k = getApiKey();
            if (k) void load(k);
          }} />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-16">
      <Header
        project={project}
        onSignOut={() => {
          clearApiKey();
          setKeyState(null);
          setProject(null);
          setRuns([]);
        }}
      />

      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              Audit history
            </h1>
            <p className="mt-1 text-sm text-ink-400">
              {runs.length} run{runs.length === 1 ? "" : "s"}
              {passRate != null && (
                <>
                  {" "}
                  · pass rate{" "}
                  <span className="font-mono text-ink-200">
                    {(passRate * 100).toFixed(0)}%
                  </span>
                </>
              )}
              {loading && <span className="ml-2 text-ink-500">Refreshing…</span>}
            </p>
          </div>
          <button
            type="button"
            onClick={() => apiKey && void load(apiKey)}
            className="rounded-lg border border-ink-700 px-3 py-1.5 text-xs text-ink-300 hover:border-ink-500 hover:text-white"
          >
            Refresh
          </button>
        </div>

        {error && (
          <p className="mt-4 rounded-lg border border-fail/30 bg-fail/10 px-3 py-2 text-sm text-red-300">
            {error}
          </p>
        )}

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            label="Faithfulness"
            latest={latest?.faithfulness_mean ?? null}
            series={series.faithfulness}
            accent="#a78bfa"
          />
          <MetricCard
            label="Answer relevancy"
            latest={latest?.answer_relevancy_mean ?? null}
            series={series.relevancy}
            accent="#38bdf8"
          />
          <MetricCard
            label="Prompt injection"
            latest={latest?.prompt_injection_mean ?? null}
            series={series.injection}
            accent="#34d399"
          />
          <div className="rounded-2xl border border-ink-800/80 bg-ink-900/60 p-4 backdrop-blur">
            <p className="text-xs font-medium uppercase tracking-wider text-ink-400">
              Latest run
            </p>
            {latest ? (
              <>
                <p
                  className={`mt-1 text-2xl font-semibold ${
                    latest.overall_passed ? "text-pass" : "text-fail"
                  }`}
                >
                  {latest.overall_passed ? "PASSED" : "FAILED"}
                </p>
                <p className="mt-1 truncate font-mono text-xs text-ink-400">
                  {latest.exit_reason}
                </p>
              </>
            ) : (
              <p className="mt-1 text-2xl text-ink-500">—</p>
            )}
          </div>
        </div>

        <section className="mt-8">
          <h2 className="mb-3 text-sm font-medium uppercase tracking-wide text-ink-400">
            Recent runs
          </h2>
          <RunsTable runs={runs} />
        </section>
      </main>
    </div>
  );
}
