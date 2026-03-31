import { useEffect, useState } from "react";
import Loading from "../components/ui/Loading";
import {
  getSuppliers,
  getItems,
  getQuotes,
  getPurchases,
} from "../api/endpoints";
import type { Supplier, Item, Quote, Purchase } from "../types";

type Tab = "suppliers" | "items" | "quotes" | "purchases";

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: "suppliers", label: "Fornecedores", icon: "🏭" },
  { id: "items", label: "Itens", icon: "📦" },
  { id: "quotes", label: "Cotações", icon: "📋" },
  { id: "purchases", label: "Compras", icon: "🛒" },
];

export default function Data() {
  const [activeTab, setActiveTab] = useState<Tab>("suppliers");
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getSuppliers(), getItems(), getQuotes(), getPurchases()]).then(
      ([s, i, q, p]) => {
        setSuppliers(s || []);
        setItems(i || []);
        setQuotes(q || []);
        setPurchases(p || []);
        setLoading(false);
      },
    );
  }, []);

  if (loading) return <Loading />;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Dados Cadastrados</h1>
        <p className="text-slate-400 text-sm mt-1">
          Dados carregados da API REST
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition ${
              activeTab === tab.id
                ? "bg-blue-600/15 text-blue-400 border border-blue-500/20"
                : "bg-slate-800/50 text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tabela */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        {activeTab === "suppliers" && <SuppliersTable data={suppliers} />}
        {activeTab === "items" && <ItemsTable data={items} />}
        {activeTab === "quotes" && (
          <QuotesTable data={quotes} suppliers={suppliers} items={items} />
        )}
        {activeTab === "purchases" && (
          <PurchasesTable
            data={purchases}
            suppliers={suppliers}
            items={items}
          />
        )}
      </div>
    </div>
  );
}

// ── Tabelas ──

function SuppliersTable({ data }: { data: Supplier[] }) {
  if (data.length === 0)
    return <EmptyState text="Nenhum fornecedor cadastrado." />;
  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-slate-800">
          <Th>Nome</Th>
          <Th>Cidade</Th>
          <Th>UF</Th>
          <Th>Prazo Entrega</Th>
          <Th>Condição</Th>
        </tr>
      </thead>
      <tbody>
        {data.map((s) => (
          <tr
            key={s.id}
            className="border-b border-slate-800/50 hover:bg-slate-800/30"
          >
            <Td bold>{s.name}</Td>
            <Td>{s.city}</Td>
            <Td>{s.state}</Td>
            <Td>{s.avg_delivery_days} dias</Td>
            <Td>{s.payment_terms}</Td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan={5} className="px-5 py-3 text-xs text-slate-500">
            {data.length} fornecedores
          </td>
        </tr>
      </tfoot>
    </table>
  );
}

function ItemsTable({ data }: { data: Item[] }) {
  if (data.length === 0) return <EmptyState text="Nenhum item cadastrado." />;
  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-slate-800">
          <Th>Nome</Th>
          <Th>Categoria</Th>
          <Th>Unidade</Th>
          <Th>Preço Médio</Th>
        </tr>
      </thead>
      <tbody>
        {data.map((i) => (
          <tr
            key={i.id}
            className="border-b border-slate-800/50 hover:bg-slate-800/30"
          >
            <Td bold>{i.name}</Td>
            <Td>
              <span className="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded-lg">
                {i.category}
              </span>
            </Td>
            <Td>{i.unit}</Td>
            <Td>
              {i.current_avg_price > 0
                ? `R$ ${i.current_avg_price.toFixed(2)}`
                : "—"}
            </Td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan={4} className="px-5 py-3 text-xs text-slate-500">
            {data.length} itens
          </td>
        </tr>
      </tfoot>
    </table>
  );
}

function QuotesTable({
  data,
  suppliers,
  items,
}: {
  data: Quote[];
  suppliers: Supplier[];
  items: Item[];
}) {
  if (data.length === 0)
    return <EmptyState text="Nenhuma cotação registrada." />;

  const getName = (list: { id: number; name: string }[], id: number) =>
    list.find((x) => x.id === id)?.name || `#${id}`;

  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-slate-800">
          <Th>Item</Th>
          <Th>Fornecedor</Th>
          <Th>Preço/un</Th>
          <Th>Frete</Th>
          <Th>Prazo</Th>
          <Th>Total</Th>
          <Th>Data</Th>
        </tr>
      </thead>
      <tbody>
        {data.slice(0, 50).map((q) => (
          <tr
            key={q.id}
            className="border-b border-slate-800/50 hover:bg-slate-800/30"
          >
            <Td bold>{getName(items, q.item_id)}</Td>
            <Td>{getName(suppliers, q.supplier_id)}</Td>
            <Td>R$ {q.unit_price.toFixed(2)}</Td>
            <Td>R$ {q.freight.toFixed(2)}</Td>
            <Td>{q.delivery_days}d</Td>
            <Td bold>
              R${" "}
              {q.total_cost.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </Td>
            <Td>{q.date}</Td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan={7} className="px-5 py-3 text-xs text-slate-500">
            {data.length} cotações {data.length > 50 && "(mostrando 50)"}
          </td>
        </tr>
      </tfoot>
    </table>
  );
}

function PurchasesTable({
  data,
  suppliers,
  items,
}: {
  data: Purchase[];
  suppliers: Supplier[];
  items: Item[];
}) {
  if (data.length === 0)
    return <EmptyState text="Nenhuma compra registrada." />;

  const getName = (list: { id: number; name: string }[], id: number) =>
    list.find((x) => x.id === id)?.name || `#${id}`;

  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-slate-800">
          <Th>Item</Th>
          <Th>Fornecedor</Th>
          <Th>Qtd</Th>
          <Th>Preço/un</Th>
          <Th>Total</Th>
          <Th>Status</Th>
          <Th>Data</Th>
        </tr>
      </thead>
      <tbody>
        {data.map((p) => (
          <tr
            key={p.id}
            className="border-b border-slate-800/50 hover:bg-slate-800/30"
          >
            <Td bold>{getName(items, p.item_id)}</Td>
            <Td>{getName(suppliers, p.supplier_id)}</Td>
            <Td>{p.quantity}</Td>
            <Td>R$ {p.unit_price.toFixed(2)}</Td>
            <Td bold>
              R${" "}
              {p.total_cost.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
              })}
            </Td>
            <Td>
              <span
                className={`text-xs px-2.5 py-1 rounded-lg ${
                  p.status === "concluida"
                    ? "bg-green-500/15 text-green-400"
                    : p.status === "pendente"
                      ? "bg-amber-500/15 text-amber-400"
                      : "bg-red-500/15 text-red-400"
                }`}
              >
                {p.status}
              </span>
            </Td>
            <Td>{p.date}</Td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td colSpan={7} className="px-5 py-3 text-xs text-slate-500">
            {data.length} compras
          </td>
        </tr>
      </tfoot>
    </table>
  );
}

// ── Componentes auxiliares ──

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
      {children}
    </th>
  );
}

function Td({ children, bold }: { children: React.ReactNode; bold?: boolean }) {
  return (
    <td
      className={`px-5 py-3.5 text-sm ${bold ? "text-white font-medium" : "text-slate-300"}`}
    >
      {children}
    </td>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="p-10 text-center text-slate-500 text-sm">{text}</div>;
}
