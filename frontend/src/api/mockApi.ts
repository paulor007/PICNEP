/**
 * Camada de API simulada — substitui chamadas reais ao backend por dados em memória.
 * Simula atraso de rede (200-400 ms) para manter os estados de carregamento visíveis.
 */

import type {
  Supplier,
  Item,
  Quote,
  Purchase,
  Recommendation,
  Alert,
  CostRanking,
  User,
  LoginResponse,
} from "../types";

import {
  suppliers,
  items,
  quotes,
  purchases,
  recommendations,
  alerts as initialAlerts,
  costRankings,
  opportunities,
  users as initialUsers,
  credentials,
} from "../data/mockData";

// ── Helpers ──────────────────────────────────────────────────

function delay(ms?: number): Promise<void> {
  const t = ms ?? 200 + Math.random() * 200; // 200-400ms
  return new Promise((resolve) => setTimeout(resolve, t));
}

// In-memory mutable copies so "create" actions persist during session
let alertsStore: Alert[] = [...initialAlerts];
let usersStore: User[] = [...initialUsers];
let nextAlertId = initialAlerts.length + 1;
let nextUserId = initialUsers.length + 1;

// ── Data endpoints ───────────────────────────────────────────

export async function getSuppliers(): Promise<Supplier[]> {
  await delay();
  return suppliers;
}

export async function getItems(): Promise<Item[]> {
  await delay();
  return items;
}

export async function getQuotes(): Promise<Quote[]> {
  await delay();
  return quotes;
}

export async function getPurchases(): Promise<Purchase[]> {
  await delay();
  return purchases;
}

// ── Analysis endpoints ───────────────────────────────────────

export async function getRecommendations(): Promise<Recommendation[]> {
  await delay();
  return recommendations;
}

export async function getOpportunities(): Promise<
  { economia_potencial: number }[]
> {
  await delay();
  return opportunities;
}

export async function getCostRanking(itemId: number): Promise<CostRanking[]> {
  await delay();
  return costRankings[itemId] || [];
}

// ── Alerts ───────────────────────────────────────────────────

export async function getAlerts(): Promise<Alert[]> {
  await delay();
  return [...alertsStore].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );
}

export async function generateAlerts(): Promise<{ total: number }> {
  await delay(600);
  const newAlerts: Alert[] = [
    {
      id: nextAlertId++,
      type: "oportunidade_compra",
      severity: "info",
      message:
        "Nova oportunidade: Tubo PVC 100mm na TubAço Taguatinga a R$ 52,00/barra. CET 10% abaixo da média.",
      data: { economia_potencial: 310 },
      is_read: false,
      created_at: new Date().toISOString(),
    },
    {
      id: nextAlertId++,
      type: "preco_subiu",
      severity: "warning",
      message:
        "Areia Lavada subiu 4% na DF Materiais Guará (de R$ 168,00 para R$ 175,00/m³).",
      data: null,
      is_read: false,
      created_at: new Date().toISOString(),
    },
  ];
  alertsStore = [...alertsStore, ...newAlerts];
  return { total: alertsStore.length };
}

// ── Users (admin) ────────────────────────────────────────────

export async function getUsers(): Promise<User[]> {
  await delay();
  return usersStore;
}

export async function createUser(data: {
  name: string;
  email: string;
  password: string;
  role: string;
}): Promise<User> {
  await delay(400);
  const newUser: User = {
    id: nextUserId++,
    name: data.name,
    email: data.email,
    role: data.role as User["role"],
    is_active: true,
  };
  usersStore = [...usersStore, newUser];
  return newUser;
}

export async function deactivateUser(
  userId: number,
  active: boolean,
): Promise<void> {
  await delay(300);
  usersStore = usersStore.map((u) =>
    u.id === userId ? { ...u, is_active: active } : u,
  );
}

export async function deleteUser(userId: number): Promise<void> {
  await delay(300);
  usersStore = usersStore.filter((u) => u.id !== userId);
}

// ── Auth ─────────────────────────────────────────────────────

export async function mockLogin(
  email: string,
  password: string,
): Promise<LoginResponse | null> {
  await delay(400);
  const cred = credentials[email];
  if (!cred || cred.password !== password) return null;

  const user = initialUsers[cred.userId];
  if (!user) return null;

  return {
    access_token: `demo_token_${user.role}_${Date.now()}`,
    token_type: "bearer",
    role: user.role,
    name: user.name,
  };
}
