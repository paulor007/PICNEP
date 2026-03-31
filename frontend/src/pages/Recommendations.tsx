import { useEffect, useState } from "react";
import Loading from "../components/ui/Loading";
import { getRecommendations, getItems, getCostRanking } from "../api/endpoints";
import type { Recommendation, Item, CostRanking } from "../types";

const actionConfig = {
  comprar_agora: {
    icon: "🟢",
    label: "COMPRAR AGORA",
    bg: "bg-green-500/10 border-green-500/20",
  },
  renegociar: {
    icon: "🟡",
    label: "RENEGOCIAR",
    bg: "bg-amber-500/10 border-amber-500/20",
  },
  esperar: {
    icon: "🔴",
    label: "ESPERAR",
    bg: "bg-red-500/10 border-red-500/20",
  },
  pedir_cotacao: {
    icon: "⚪",
    label: "PEDIR COTAÇÃO",
    bg: "bg-slate-500/10 border-slate-500/20",
  },
};

export default function Recommendations() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [selectedItem, setSelectedItem] = useState<number | null>(null);
  const [ranking, setRanking] = useState<CostRanking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const [r, i] = await Promise.all([getRecommendations(), getItems()]);
      setRecs(r || []);
      setItems(i || []);
      setLoading(false);
    }
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedItem) {
      getCostRanking(selectedItem).then((r) => setRanking(r || []));
    }
  }, [selectedItem]);

  if (loading) return <Loading />;

  // Contar ações
  const actionCounts: Record<string, number> = {};
  recs.forEach((r) => {
    if (!("erro" in r)) {
      actionCounts[r.acao] = (actionCounts[r.acao] || 0) + 1;
    }
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">
          Recomendações de Compra
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Baseadas no Custo Efetivo Total (preço + frete + condição de
          pagamento)
        </p>
      </div>

      {/* Cards resumo */}
      {Object.keys(actionCounts).length > 0 && (
        <div className="flex gap-4 mb-8 flex-wrap">
          {Object.entries(actionCounts).map(([acao, count]) => {
            const cfg =
              actionConfig[acao as keyof typeof actionConfig] ||
              actionConfig.pedir_cotacao;
            return (
              <div
                key={acao}
                className={`${cfg.bg} border rounded-xl px-5 py-3 flex items-center gap-3`}
              >
                <span className="text-xl">{cfg.icon}</span>
                <div>
                  <p className="text-white font-bold text-lg">{count}</p>
                  <p className="text-slate-400 text-xs">{cfg.label}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Lista de recomendações */}
      {recs.length > 0 ? (
        <div className="space-y-3 mb-10">
          {recs.map((rec, i) => {
            if ("erro" in rec) return null;
            const cfg =
              actionConfig[rec.acao as keyof typeof actionConfig] ||
              actionConfig.pedir_cotacao;
            return (
              <div key={i} className={`${cfg.bg} border rounded-2xl p-5`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{cfg.icon}</span>
                    <div>
                      <h3 className="text-white font-semibold">
                        {rec.item_name}
                      </h3>
                      <span className="text-xs font-medium text-slate-400">
                        {cfg.label}
                      </span>
                    </div>
                  </div>
                  {rec.economia_potencial > 0 && (
                    <span className="text-green-400 font-bold text-sm">
                      💰 R${" "}
                      {rec.economia_potencial.toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </span>
                  )}
                </div>
                <p className="text-slate-400 text-sm">{rec.motivo}</p>
                {rec.fornecedor_ideal && (
                  <p className="text-slate-500 text-xs mt-1">
                    Fornecedor ideal:{" "}
                    <span className="text-white">{rec.fornecedor_ideal}</span>
                  </p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center mb-10">
          <p className="text-slate-400">
            Sem recomendações. Cadastre cotações e compras.
          </p>
        </div>
      )}

      {/* Ranking por Custo Efetivo Total */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white mb-1">
          Ranking por Custo Efetivo Total
        </h2>
        <p className="text-slate-500 text-xs mb-4">
          Não é só preço unitário. Inclui frete + benefício do prazo de
          pagamento.
        </p>

        {items.length > 0 && (
          <select
            value={selectedItem || ""}
            onChange={(e) => setSelectedItem(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white mb-4 focus:outline-none focus:border-blue-500"
          >
            <option value="">Selecione um item...</option>
            {items.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        )}

        {ranking.length > 0 ? (
          <div className="space-y-2">
            {ranking.map((r, i) => {
              const medal = ["🥇", "🥈", "🥉"][i] || `#${i + 1}`;
              return (
                <div
                  key={i}
                  className={`flex items-center gap-4 p-4 rounded-xl ${
                    i === 0
                      ? "bg-blue-500/10 border border-blue-500/20"
                      : "bg-slate-800/50"
                  }`}
                >
                  <span className="text-xl w-8 text-center">{medal}</span>
                  <div className="flex-1">
                    <p className="text-white font-medium">{r.supplier_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-bold">
                      R${" "}
                      {r.custo_real.toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                      })}
                    </p>
                    <p className="text-slate-500 text-xs">
                      Frete: R$ {r.custo_frete.toFixed(2)} | Prazo:{" "}
                      {r.dias_pagamento} dias
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        ) : selectedItem ? (
          <p className="text-slate-500 text-sm">Sem cotações para este item.</p>
        ) : null}
      </div>
    </div>
  );
}
