/**
 * Cliente HTTP para consumir a API FastAPI.
 *
 * - Guarda o JWT no localStorage
 * - Adiciona Bearer token em toda requisição
 * - Se receber 401 (token expirado), redireciona para login
 */

class ApiClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem("picnep_token");
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem("picnep_token", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("picnep_token");
    localStorage.removeItem("picnep_user");
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
      console.log(
        `[API] GET ${endpoint} | Token: ${this.token ? "SIM" : "NÃO"}`,
      );
      const res = await fetch(endpoint, { headers: this.headers() });
      console.log(`[API] ${endpoint} → ${res.status}`);
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
