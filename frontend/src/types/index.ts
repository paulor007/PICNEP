export interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "gestor" | "analista";
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  name: string;
}

export interface Supplier {
  id: number;
  name: string;
  city: string;
  state: string;
  avg_delivery_days: number;
  payment_terms: string;
  rating_score: number;
  is_active: boolean;
}

export interface Item {
  id: number;
  name: string;
  category: string;
  unit: string;
  current_avg_price: number;
}

export interface Quote {
  id: number;
  item_id: number;
  supplier_id: number;
  unit_price: number;
  freight: number;
  delivery_days: number;
  total_cost: number;
  date: string;
}

export interface Purchase {
  id: number;
  item_id: number;
  supplier_id: number;
  quantity: number;
  unit_price: number;
  total_cost: number;
  date: string;
  status: string;
}

export interface Recommendation {
  item_id: number;
  item_name: string;
  acao: "comprar_agora" | "renegociar" | "esperar" | "pedir_cotacao";
  motivo: string;
  fornecedor_ideal: string | null;
  economia_potencial: number;
}

export interface Alert {
  id: number;
  type: string;
  severity: "info" | "warning" | "critical";
  message: string;
  data: { economia_potencial?: number } | null;
  is_read: boolean;
  created_at: string;
}

export interface CostRanking {
  supplier_name: string;
  supplier_id: number;
  custo_real: number;
  custo_unitario_real: number;
  custo_frete: number;
  dias_pagamento: number;
  custo_bruto: number;
  beneficio_prazo: number;
}
