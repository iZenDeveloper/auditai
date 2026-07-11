"use client";

type Props = {
  values: Array<number | null | undefined>;
  width?: number;
  height?: number;
  stroke?: string;
  fill?: string;
  className?: string;
};

/** Pure SVG sparkline — no chart library. Nulls are skipped in path. */
export function Sparkline({
  values,
  width = 120,
  height = 36,
  stroke = "currentColor",
  fill = "none",
  className,
}: Props) {
  const pts = values
    .map((v, i) => (v == null || Number.isNaN(v) ? null : { i, v: Number(v) }))
    .filter((p): p is { i: number; v: number } => p !== null);

  if (pts.length < 2) {
    return (
      <svg width={width} height={height} className={className} aria-hidden>
        <line
          x1={0}
          y1={height / 2}
          x2={width}
          y2={height / 2}
          stroke={stroke}
          strokeOpacity={0.25}
          strokeWidth={1}
        />
      </svg>
    );
  }

  const min = Math.min(...pts.map((p) => p.v));
  const max = Math.max(...pts.map((p) => p.v));
  const range = max - min || 1;
  const pad = 2;

  const coords = pts.map((p, idx) => {
    const x =
      pad + (idx / (pts.length - 1)) * (width - pad * 2);
    const y =
      height - pad - ((p.v - min) / range) * (height - pad * 2);
    return { x, y };
  });

  const d = coords
    .map((c, i) => `${i === 0 ? "M" : "L"} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`)
    .join(" ");

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      role="img"
      aria-label="Sparkline"
    >
      {fill !== "none" && (
        <path
          d={`${d} L ${coords[coords.length - 1].x} ${height} L ${coords[0].x} ${height} Z`}
          fill={fill}
          opacity={0.15}
        />
      )}
      <path d={d} fill="none" stroke={stroke} strokeWidth={1.75} strokeLinejoin="round" strokeLinecap="round" />
      <circle
        cx={coords[coords.length - 1].x}
        cy={coords[coords.length - 1].y}
        r={2.5}
        fill={stroke}
      />
    </svg>
  );
}
