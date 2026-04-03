import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Building2, LogIn } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("paulo@construtora.com");
  const [password, setPassword] = useState("senha123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const ok = await login(email, password);
    setLoading(false);

    if (ok) {
      navigate("/");
    } else {
      setError("Email ou senha incorretos.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Demo banner */}
      <div className="bg-blue-600/10 border-b border-blue-500/20 px-4 py-2 text-center">
        <p className="text-blue-400/80 text-xs font-medium tracking-wide">
          🔍 Demonstração — dados simulados de uma construtora
        </p>
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600/20 mb-4">
              <Building2 className="w-8 h-8 text-blue-500" />
            </div>
            <h1 className="text-3xl font-bold text-white">PICNEP</h1>
            <p className="text-slate-400 mt-2">
              Inteligência de Compras para PMEs
            </p>
            <p className="text-slate-500 text-sm mt-1">
              Custo Efetivo Total • Engine de Recomendação
            </p>
          </div>

          {/* Card do form */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Login</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
                  placeholder="seu@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-1.5">
                  Senha
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
                  placeholder="••••••"
                  required
                />
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-3 rounded-xl transition flex items-center justify-center gap-2 mt-2"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <LogIn className="w-4 h-4" />
                    Entrar
                  </>
                )}
              </button>
            </form>

            {/* Credenciais demo */}
            <div className="mt-6 pt-6 border-t border-slate-800">
              <p className="text-slate-500 text-xs font-medium mb-2">
                Contas demo:
              </p>
              <p className="text-slate-400 text-xs">
                <span className="text-slate-500">Admin:</span>{" "}
                paulo@construtora.com / senha123
              </p>
              <p className="text-slate-400 text-xs">
                <span className="text-slate-500">Gestor:</span>{" "}
                maria@construtora.com / senha123
              </p>
              <p className="text-slate-400 text-xs">
                <span className="text-slate-500">Analista:</span>{" "}
                joao@construtora.com / senha123
              </p>
            </div>
          </div>

          {/* Rodapé */}
          <p className="text-center text-slate-600 text-xs mt-6">
            Desenvolvido por Paulo Lavarini
          </p>
        </div>
      </div>
    </div>
  );
}
