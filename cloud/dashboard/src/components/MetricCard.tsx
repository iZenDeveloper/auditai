"use client";

import { Sparkline } from "./Sparkline";

type Props = {
  label: string;
  latest: number | null;
  series: Array<number | null>;
  accent?: string;
};

function fmt(n: number | null): string {
  if (n == null) return "—";
  return n.toFixed(2);
}

export function MetricCard({ label, latest, series, accent = "#a78bfa" }: Props) {
  const trend =
    series.filter((x) => x != null).length >= 2
      ? (series[series.length - 1] ?? 0) - (series[0] ?? 0)
      : 0;

  return (
    <div className="rounded-2xl border border-ink-800/80 bg-ink-900/60 p-4 backdrop-blur">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-ink-400">
            {label}
          </p>
          <p className="mt-1 font-mono text-2xl font-semibold tabular-nums text-white">
            {fmt(latest)}
          </p>
          {series.length >= 2 && (
            <p
              className={`mt-1 text-xs tabular-nums ${
                trend >= 0 ? "text-pass" : "text-fail"
              }`}
            >
              {trend >= 0 ? "▲" : "▼"} {Math.abs(trend).toFixed(2)} vs oldest
            </p>
          )}
        </div>
        <div className="text-accent-soft">
          <Sparkline values={series} stroke={accent} width={100} height={40} />
        </div>
      </div>
    </div>
  );
}
