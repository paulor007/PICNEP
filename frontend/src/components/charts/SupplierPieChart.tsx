import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { Quote, Supplier } from "../../types";

interface Props {
  quotes: Quote[];
  suppliers: Supplier[];
}

const COLORS = [
  "#3b82f6",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

export default function SupplierPieChart({ quotes, suppliers }: Props) {
  // Contar cotações por fornecedor
  const countMap: Record<string, number> = {};
  quotes.forEach((q) => {
    const supplier = suppliers.find((s) => s.id === q.supplier_id);
    const name = supplier?.name || `Forn. ${q.supplier_id}`;
    countMap[name] = (countMap[name] || 0) + 1;
  });

  const data = Object.entries(countMap).map(([name, value]) => ({
    name,
    value,
  }));

  if (data.length === 0)
    return <p className="text-slate-500 text-sm">Sem dados</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          dataKey="value"
          stroke="none"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "12px",
            color: "#e2e8f0",
          }}
        />
        <Legend wrapperStyle={{ color: "#94a3b8", fontSize: "12px" }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
