const KEY = "auditai_project_key";

export function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(KEY);
}

export function setApiKey(key: string): void {
  sessionStorage.setItem(KEY, key.trim());
}

export function clearApiKey(): void {
  sessionStorage.removeItem(KEY);
}
