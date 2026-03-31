import { useEffect, useState } from "react";
import Loading from "../components/ui/Loading";
import { getAlerts, generateAlerts } from "../api/endpoints";
import type { Alert } from "../types";
import { useAuth } from "../context/AuthContext";

const severityConfig = {
  info: {
    icon: "🟢",
    label: "Info",
    bg: "bg-green-500/10 border-green-500/20",
  },
  warning: {
    icon: "🟡",
    label: "Atenção",
    bg: "bg-amber-500/10 border-amber-500/20",
  },
  critical: {
    icon: "🔴",
    label: "Crítico",
    bg: "bg-red-500/10 border-red-500/20",
  },
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    getAlerts().then((data) => {
      setAlerts(data || []);
      setLoading(false);
    });
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    const result = await generateAlerts();
    if (result) {
      const data = await getAlerts();
      setAlerts(data || []);
    }
    setGenerating(false);
  };

  if (loading) return <Loading />;

  // Contar por severidade
  const severityCounts: Record<string, number> = {};
  alerts.forEach((a) => {
    severityCounts[a.severity] = (severityCounts[a.severity] || 0) + 1;
  });

  return (
    <div>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Alertas Inteligentes
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Gerados automaticamente pela engine de análise
          </p>
        </div>
        {(user?.role === "admin" || user?.role === "gestor") && (
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition flex items-center gap-2"
          >
            {generating ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              "🔄"
            )}
            Gerar Alertas
          </button>
        )}
      </div>

      {/* Cards de severidade */}
      <div className="flex gap-4 mb-8">
        {Object.entries(severityConfig).map(([key, cfg]) => (
          <div
            key={key}
            className={`${cfg.bg} border rounded-xl px-5 py-3 flex items-center gap-3`}
          >
            <span className="text-xl">{cfg.icon}</span>
            <div>
              <p className="text-white font-bold text-lg">
                {severityCounts[key] || 0}
              </p>
              <p className="text-slate-400 text-xs">{cfg.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Lista de alertas */}
      {alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => {
            const cfg =
              severityConfig[alert.severity as keyof typeof severityConfig] ||
              severityConfig.info;
            const economia =
              alert.data && typeof alert.data === "object"
                ? alert.data.economia_potencial || 0
                : 0;

            return (
              <div
                key={alert.id}
                className={`${cfg.bg} border rounded-2xl p-5`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-xl mt-0.5">{cfg.icon}</span>
                    <div>
                      <span className="text-xs font-semibold text-slate-400 uppercase">
                        {alert.type.replace(/_/g, " ")}
                      </span>
                      <p className="text-white mt-1">{alert.message}</p>
                      {economia > 0 && (
                        <p className="text-green-400 text-sm mt-1">
                          💰 Economia potencial: R${" "}
                          {economia.toLocaleString("pt-BR", {
                            minimumFractionDigits: 2,
                          })}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          <p className="text-slate-600 text-xs text-center pt-2">
            Total: {alerts.length} alertas
          </p>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
          <p className="text-slate-400">
            Sem alertas. Clique em "Gerar Alertas" para analisar os dados.
          </p>
        </div>
      )}
    </div>
  );
}
