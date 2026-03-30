import { api } from "./client";
import type {
  Supplier,
  Item,
  Quote,
  Purchase,
  Recommendation,
  Alert,
  User,
  CostRanking,
} from "../types";

// ── Dados ──
export const getSuppliers = () => api.get<Supplier[]>("/api/v1/suppliers/");
export const getItems = () => api.get<Item[]>("/api/v1/items/");
export const getQuotes = () => api.get<Quote[]>("/api/v1/quotes/");
export const getPurchases = () => api.get<Purchase[]>("/api/v1/purchases/");

// ── Análise ──
export const getRecommendations = async (): Promise<Recommendation[]> => {
  const data = await api.get<{ recommendations: Recommendation[] }>(
    "/api/v1/analysis/recommendations",
  );
  return data?.recommendations || [];
};

export const getOpportunities = async () => {
  const data = await api.get<{
    opportunities: { economia_potencial: number }[];
  }>("/api/v1/analysis/opportunities");
  return data?.opportunities || [];
};

export const getCostRanking = async (
  itemId: number,
): Promise<CostRanking[]> => {
  const data = await api.get<{ ranking: CostRanking[] }>(
    `/api/v1/analysis/cost/${itemId}`,
  );
  return data?.ranking || [];
};

// ── Alertas ──
export const getAlerts = async (): Promise<Alert[]> => {
  const data = await api.get<{ alerts: Alert[] }>("/api/v1/alerts");
  return data?.alerts || [];
};

export const generateAlerts = () =>
  api.post<{ total: number }>("/api/v1/analysis/alerts/generate");

// ── Usuários (admin) ──
export const getUsers = () => api.get<User[]>("/api/v1/users");
export const createUser = (data: {
  name: string;
  email: string;
  password: string;
  role: string;
}) => api.post("/api/v1/users", data);
