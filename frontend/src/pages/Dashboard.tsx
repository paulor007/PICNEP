import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import Loading from "../components/ui/Loading";
import SupplierPieChart from "../components/charts/SupplierPieChart";
import ItemBarChart from "../components/charts/ItemBarChart";
import {
  getSuppliers,
  getItems,
  getQuotes,
  getPurchases,
  getOpportunities,
} from "../api/endpoints";
import type { Supplier, Item, Quote, Purchase } from "../types";

export default function Dashboard() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [economia, setEconomia] = useState(0);
  const [oppCount, setOppCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const [s, i, q, p, o] = await Promise.all([
        getSuppliers(),
        getItems(),
        getQuotes(),
        getPurchases(),
        getOpportunities(),
      ]);
      setSuppliers(s || []);
      setItems(i || []);
      setQuotes(q || []);
      setPurchases(p || []);
      if (o && o.length > 0) {
        setEconomia(
          o.reduce((acc, opp) => acc + (opp.economia_potencial || 0), 0),
        );
        setOppCount(o.length);
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  if (loading) return <Loading />;

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Visão Geral</h1>
        <p className="text-slate-400 text-sm mt-1">
          Custo Efetivo Total • Recomendações • Alertas
        </p>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card
          icon="🏭"
          label="Fornecedores"
          value={suppliers.length}
          color="blue"
        />
        <Card icon="📦" label="Itens" value={items.length} color="green" />
        <Card icon="📋" label="Cotações" value={quotes.length} color="amber" />
        <Card
          icon="🛒"
          label="Compras"
          value={purchases.length}
          color="purple"
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Cotações por Fornecedor
          </h3>
          <SupplierPieChart quotes={quotes} suppliers={suppliers} />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Maiores Valores Cotados
          </h3>
          <ItemBarChart quotes={quotes} items={items} />
        </div>
      </div>

      {/* Economia Potencial */}
      {economia > 0 && (
        <div className="bg-linear-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-2xl p-6">
          <div className="flex items-center gap-3">
            <span className="text-3xl">💰</span>
            <div>
              <h3 className="text-xl font-bold text-white">
                Economia Potencial: R${" "}
                {economia.toLocaleString("pt-BR", {
                  minimumFractionDigits: 2,
                })}
              </h3>
              <p className="text-green-400 text-sm">
                {oppCount} oportunidades detectadas. Veja na aba Recomendações.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
