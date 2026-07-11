"use client";

import Link from "next/link";
import type { ProjectInfo } from "@/lib/types";

type Props = {
  project?: ProjectInfo | null;
  onSignOut?: () => void;
};

export function Header({ project, onSignOut }: Props) {
  return (
    <header className="border-b border-ink-800/80 bg-ink-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/20 text-sm">
            🛡️
          </span>
          <div>
            <p className="text-sm font-semibold tracking-tight text-white group-hover:text-accent-soft">
              AuditAI Cloud
            </p>
            <p className="text-[11px] text-ink-400">Run history · metrics</p>
          </div>
        </Link>

        {project && (
          <div className="flex items-center gap-3 text-sm">
            <div className="hidden text-right sm:block">
              <p className="font-medium text-ink-100">{project.name}</p>
              <p className="font-mono text-[11px] text-ink-400">
                {project.api_key_prefix}…
              </p>
            </div>
            {onSignOut && (
              <button
                type="button"
                onClick={onSignOut}
                className="rounded-lg border border-ink-700 px-3 py-1.5 text-xs text-ink-300 transition hover:border-ink-500 hover:text-white"
              >
                Sign out
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
