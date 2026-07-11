"use client";

import Link from "next/link";
import type { RunSummary } from "@/lib/types";

type Props = {
  runs: RunSummary[];
};

function fmtScore(n: number | null): string {
  return n == null ? "—" : n.toFixed(2);
}

function shortSha(sha: string | null): string {
  if (!sha) return "—";
  return sha.slice(0, 7);
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function RunsTable({ runs }: Props) {
  if (runs.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-ink-700 bg-ink-900/40 px-6 py-12 text-center">
        <p className="text-ink-300">No runs yet</p>
        <p className="mt-1 text-sm text-ink-500">
          Push from CLI with <code className="text-ink-300">AUDITAI_PROJECT_KEY</code>
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-ink-800 bg-ink-900/50">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-ink-800 bg-ink-900/80 text-xs uppercase tracking-wide text-ink-400">
            <tr>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">When</th>
              <th className="px-4 py-3 font-medium">Faith.</th>
              <th className="px-4 py-3 font-medium">Relev.</th>
              <th className="px-4 py-3 font-medium">Inject.</th>
              <th className="px-4 py-3 font-medium">Cases</th>
              <th className="px-4 py-3 font-medium">Git</th>
              <th className="px-4 py-3 font-medium" />
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-800/80">
            {runs.map((run) => (
              <tr key={run.id} className="hover:bg-ink-800/30">
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium ${
                      run.overall_passed
                        ? "bg-pass/15 text-green-300"
                        : "bg-fail/15 text-red-300"
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        run.overall_passed ? "bg-pass" : "bg-fail"
                      }`}
                    />
                    {run.overall_passed ? "PASS" : "FAIL"}
                  </span>
                </td>
                <td className="px-4 py-3 text-ink-300">{fmtDate(run.created_at)}</td>
                <td className="px-4 py-3 font-mono tabular-nums text-ink-100">
                  {fmtScore(run.faithfulness_mean)}
                </td>
                <td className="px-4 py-3 font-mono tabular-nums text-ink-100">
                  {fmtScore(run.answer_relevancy_mean)}
                </td>
                <td className="px-4 py-3 font-mono tabular-nums text-ink-100">
                  {fmtScore(run.prompt_injection_mean)}
                </td>
                <td className="px-4 py-3 tabular-nums text-ink-300">
                  {run.total_cases}
                  {run.failed_cases > 0 && (
                    <span className="text-fail"> · {run.failed_cases} err</span>
                  )}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-ink-400">
                  {shortSha(run.git_sha)}
                </td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/runs/${run.id}`}
                    className="text-xs font-medium text-accent-soft hover:text-white"
                  >
                    Detail →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
