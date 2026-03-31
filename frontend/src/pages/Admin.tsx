import { useEffect, useState } from "react";
import Loading from "../components/ui/Loading";
import { getUsers, createUser } from "../api/endpoints";
import type { User } from "../types";
import { useAuth } from "../context/AuthContext";

const roleConfig = {
  admin: { icon: "🔴", label: "Admin", bg: "bg-red-500/15 text-red-400" },
  gestor: { icon: "🟡", label: "Gestor", bg: "bg-amber-500/15 text-amber-400" },
  analista: {
    icon: "🟢",
    label: "Analista",
    bg: "bg-green-500/15 text-green-400",
  },
};

export default function Admin() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "analista",
  });
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getUsers().then((data) => {
      setUsers(data || []);
      setLoading(false);
    });
  }, []);

  if (user?.role !== "admin") {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
        <p className="text-red-400 font-medium">
          Acesso negado. Apenas administradores podem acessar esta página.
        </p>
      </div>
    );
  }

  if (loading) return <Loading />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setFormSuccess("");
    setSubmitting(true);

    const result = await createUser(formData);
    setSubmitting(false);

    if (result) {
      setFormSuccess(`Usuário ${formData.name} criado como ${formData.role}!`);
      setFormData({ name: "", email: "", password: "", role: "analista" });
      // Recarregar lista
      const updated = await getUsers();
      setUsers(updated || []);
      setTimeout(() => {
        setShowForm(false);
        setFormSuccess("");
      }, 2000);
    } else {
      setFormError("Erro ao criar. Email pode já existir.");
    }
  };

  return (
    <div>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Gestão de Usuários</h1>
          <p className="text-slate-400 text-sm mt-1">
            Apenas administradores podem gerenciar usuários
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition"
        >
          {showForm ? "Cancelar" : "+ Novo Usuário"}
        </button>
      </div>

      {/* Formulário de criação */}
      {showForm && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            Criar Novo Usuário
          </h2>
          <form
            onSubmit={handleSubmit}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">
                Nome
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">
                Senha
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                required
                minLength={6}
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">
                Perfil
              </label>
              <select
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value })
                }
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
              >
                <option value="analista">Analista</option>
                <option value="gestor">Gestor</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div className="md:col-span-2">
              {formError && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-red-400 text-sm mb-3">
                  {formError}
                </div>
              )}
              {formSuccess && (
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-3 text-green-400 text-sm mb-3">
                  {formSuccess}
                </div>
              )}
              <button
                type="submit"
                disabled={submitting}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-6 py-3 rounded-xl transition flex items-center gap-2"
              >
                {submitting ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : null}
                Criar Usuário
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de usuários */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">
                Nome
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">
                Email
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">
                Perfil
              </th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const role =
                roleConfig[u.role as keyof typeof roleConfig] ||
                roleConfig.analista;
              return (
                <tr
                  key={u.id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30"
                >
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-white text-sm font-bold">
                        {u.name.charAt(0)}
                      </div>
                      <span className="text-white font-medium text-sm">
                        {u.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-slate-300 text-sm">
                    {u.email}
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`text-xs px-2.5 py-1 rounded-lg ${role.bg}`}
                    >
                      {role.icon} {role.label}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`text-xs px-2.5 py-1 rounded-lg ${
                        u.is_active
                          ? "bg-green-500/15 text-green-400"
                          : "bg-red-500/15 text-red-400"
                      }`}
                    >
                      {u.is_active ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={4} className="px-5 py-3 text-xs text-slate-500">
                {users.length} usuários
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      {/* Tabela de perfis */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mt-8">
        <h2 className="text-lg font-semibold text-white mb-4">
          Perfis de Acesso (RBAC)
        </h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-red-500/5 rounded-xl">
            <span className="text-xl">🔴</span>
            <div>
              <p className="text-white font-medium text-sm">Admin</p>
              <p className="text-slate-400 text-xs">
                Tudo: gerenciar usuários, CRUD, análises, configuração
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-amber-500/5 rounded-xl">
            <span className="text-xl">🟡</span>
            <div>
              <p className="text-white font-medium text-sm">Gestor</p>
              <p className="text-slate-400 text-xs">
                Dashboard, cotações, relatórios, recomendações
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-green-500/5 rounded-xl">
            <span className="text-xl">🟢</span>
            <div>
              <p className="text-white font-medium text-sm">Analista</p>
              <p className="text-slate-400 text-xs">
                Consultar dados, exportar, ver alertas (sem editar)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
