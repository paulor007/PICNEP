/**
 * Safe storage wrapper — falls back to in-memory if localStorage is unavailable
 * (e.g. sandboxed iframes, private browsing, etc.)
 */

const memoryStore: Record<string, string> = {};

function isLocalStorageAvailable(): boolean {
  try {
    const key = "__storage_test__";
    localStorage.setItem(key, "1");
    localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}

const useLocal = isLocalStorageAvailable();

export const safeStorage = {
  getItem(key: string): string | null {
    if (useLocal) return localStorage.getItem(key);
    return memoryStore[key] ?? null;
  },
  setItem(key: string, value: string): void {
    if (useLocal) localStorage.setItem(key, value);
    else memoryStore[key] = value;
  },
  removeItem(key: string): void {
    if (useLocal) localStorage.removeItem(key);
    else delete memoryStore[key];
  },
};
