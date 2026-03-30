interface CardProps {
  icon: string;
  label: string;
  value: string | number;
  color?: string;
}

export default function Card({
  icon,
  label,
  value,
  color = "blue",
}: CardProps) {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-600/15 text-blue-400",
    green: "bg-green-600/15 text-green-400",
    amber: "bg-amber-600/15 text-amber-400",
    purple: "bg-purple-600/15 text-purple-400",
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-3">
        <div
          className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg ${colorMap[color] || colorMap.blue}`}
        >
          {icon}
        </div>
        <span className="text-sm text-slate-400">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
