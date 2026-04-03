/**
 * Cliente HTTP para consumir a API FastAPI.
 *
 * - Guarda o JWT via safeStorage (localStorage com fallback in-memory)
 * - Adiciona Bearer token em toda requisição
 * - Se receber 401 (token expirado), redireciona para login
 */

import { safeStorage } from "../lib/storage";

class ApiClient {
  private log(msg: string) {
    if (import.meta.env.DEV) {
      console.log(`[PICNEP] ${msg}`);
    }
  }

  private token: string | null = null;

  constructor() {
    this.token = safeStorage.getItem("picnep_token");
  }

  setToken(token: string) {
    this.token = token;
    safeStorage.setItem("picnep_token", token);
  }

  clearToken() {
    this.token = null;
    safeStorage.removeItem("picnep_token");
    safeStorage.removeItem("picnep_user");
  }

  private headers(): HeadersInit {
    const h: HeadersInit = { "Content-Type": "application/json" };
    if (this.token) {
      h["Authorization"] = `Bearer ${this.token}`;
    }
    return h;
  }

  async get<T>(endpoint: string): Promise<T | null> {
    try {
      this.log(`GET ${endpoint}`);
      const res = await fetch(endpoint, { headers: this.headers() });
      this.log(`${endpoint} → ${res.status}`);
      if (res.status === 401) {
        return null;
      }
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  async post<T>(endpoint: string, body?: unknown): Promise<T | null> {
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: this.headers(),
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  async loginRequest(
    email: string,
    password: string,
  ): Promise<{ access_token: string; role: string; name: string } | null> {
    try {
      const res = await fetch("/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }
}

export const api = new ApiClient();
