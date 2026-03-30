import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { Quote, Item } from "../../types";

interface Props {
  quotes: Quote[];
  items: Item[];
}

export default function ItemBarChart({ quotes, items }: Props) {
  // Somar total_cost por item
  const totalMap: Record<string, number> = {};
  quotes.forEach((q) => {
    const item = items.find((i) => i.id === q.item_id);
    const name = item?.name || `Item ${q.item_id}`;
    totalMap[name] = (totalMap[name] || 0) + q.total_cost;
  });

  const data = Object.entries(totalMap)
    .map(([name, total]) => ({ name, total: Math.round(total) }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 8);

  if (data.length === 0)
    return <p className="text-slate-500 text-sm">Sem dados</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
        <XAxis
          type="number"
          tick={{ fill: "#94a3b8", fontSize: 12 }}
          axisLine={false}
          tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          axisLine={false}
          width={150}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "12px",
            color: "#e2e8f0",
          }}
          formatter={(value) => [
            `R$ ${Number(value).toLocaleString("pt-BR")}`,
            "Total",
          ]}
        />
        <Bar dataKey="total" fill="#3b82f6" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
