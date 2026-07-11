import type { ProjectInfo, RunDetail, RunSummary } from "./types";

function baseUrl(): string {
  return (
    process.env.NEXT_PUBLIC_AUDITAI_API_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8080"
  );
}

async function request<T>(
  path: string,
  apiKey: string,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(`${baseUrl()}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function fetchProject(apiKey: string): Promise<ProjectInfo> {
  return request<ProjectInfo>("/v1/projects/me", apiKey);
}

export function fetchRuns(
  apiKey: string,
  limit = 50
): Promise<RunSummary[]> {
  return request<RunSummary[]>(`/v1/runs?limit=${limit}`, apiKey);
}

export function fetchRun(apiKey: string, id: string): Promise<RunDetail> {
  return request<RunDetail>(`/v1/runs/${id}`, apiKey);
}

/** Download compliance PDF for a run (browser blob download). */
export async function downloadCompliancePdf(
  apiKey: string,
  runId: string
): Promise<void> {
  const res = await fetch(`${baseUrl()}/v1/runs/${runId}/compliance.pdf`, {
    headers: { Authorization: `Bearer ${apiKey}` },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error((await res.text()) || `HTTP ${res.status}`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `auditai-compliance-${runId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function createProject(
  name: string
): Promise<{ id: string; name: string; api_key: string }> {
  const res = await fetch(`${baseUrl()}/v1/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export { baseUrl };
