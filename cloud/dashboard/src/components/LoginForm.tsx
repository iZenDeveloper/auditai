"use client";

import { FormEvent, useState } from "react";
import { createProject, fetchProject } from "@/lib/api";
import { setApiKey } from "@/lib/auth";

type Props = {
  onSuccess: () => void;
};

export function LoginForm({ onSuccess }: Props) {
  const [key, setKey] = useState("");
  const [name, setName] = useState("my-project");
  const [error, setError] = useState<string | null>(null);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await fetchProject(key.trim());
      setApiKey(key.trim());
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid project key");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    setError(null);
    setLoading(true);
    try {
      const res = await createProject(name.trim() || "my-project");
      setCreatedKey(res.api_key);
      setKey(res.api_key);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-md">
      <div className="rounded-2xl border border-ink-800 bg-ink-900/70 p-6 shadow-2xl shadow-black/40 backdrop-blur">
        <h1 className="text-xl font-semibold text-white">Connect project</h1>
        <p className="mt-1 text-sm text-ink-400">
          Paste your <code className="text-ink-200">AUDITAI_PROJECT_KEY</code>.
          Key stays in sessionStorage only — never sent to a third party.
        </p>

        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <label className="block text-xs font-medium uppercase tracking-wide text-ink-400">
            Project API key
            <input
              type="password"
              autoComplete="off"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="aai_…"
              className="mt-1.5 w-full rounded-xl border border-ink-700 bg-ink-950 px-3 py-2.5 font-mono text-sm text-white outline-none ring-accent/40 placeholder:text-ink-500 focus:border-accent focus:ring-2"
            />
          </label>

          {error && (
            <p className="rounded-lg border border-fail/30 bg-fail/10 px-3 py-2 text-sm text-red-300">
              {error}
            </p>
          )}

          {createdKey && (
            <div className="rounded-lg border border-pass/30 bg-pass/10 px-3 py-2 text-sm text-green-200">
              <p className="font-medium">New key created — copy now:</p>
              <code className="mt-1 block break-all font-mono text-xs">{createdKey}</code>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !key.trim()}
            className="w-full rounded-xl bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-dim disabled:opacity-50"
          >
            {loading ? "Connecting…" : "Open dashboard"}
          </button>
        </form>

        <div className="mt-6 border-t border-ink-800 pt-5">
          <p className="text-xs text-ink-400">No key yet? Create a local stub project:</p>
          <div className="mt-2 flex gap-2">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="flex-1 rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-white outline-none focus:border-accent"
              placeholder="project name"
            />
            <button
              type="button"
              onClick={handleCreate}
              disabled={loading}
              className="rounded-lg border border-ink-600 px-3 py-2 text-sm text-ink-200 hover:border-ink-400 hover:text-white"
            >
              Create
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
