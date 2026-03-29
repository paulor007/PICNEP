import { useAuth } from "../context/AuthContext";
import { LogOut, Building2 } from "lucide-react";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">PICNEP</h1>
              <p className="text-slate-500 text-sm">Inteligência de Compras</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-white text-sm font-medium">{user?.name}</p>
              <p className="text-slate-500 text-xs">{user?.role}</p>
            </div>
            <button
              onClick={logout}
              className="w-9 h-9 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition"
              title="Sair"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Conteúdo placeholder */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-10 text-center">
          <div className="w-16 h-16 rounded-2xl bg-green-500/20 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">✅</span>
          </div>
          <h2 className="text-xl font-bold text-white mb-2">
            Login funcionando!
          </h2>
          <p className="text-slate-400 mb-4">
            O frontend React está consumindo a API FastAPI com autenticação JWT.
          </p>
          <div className="inline-flex gap-6 text-sm">
            <div className="text-slate-500">
              Usuário:{" "}
              <span className="text-white font-medium">{user?.email}</span>
            </div>
            <div className="text-slate-500">
              Perfil:{" "}
              <span className="text-white font-medium">{user?.role}</span>
            </div>
          </div>
          <p className="text-slate-600 text-sm mt-6">
            Dashboard completo será construído na Fase F2.
          </p>
        </div>
      </div>
    </div>
  );
}
