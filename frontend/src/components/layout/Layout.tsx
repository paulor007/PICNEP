import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";

export default function Layout() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      {/* Demo banner */}
      <div className="bg-slate-900/80 border-b border-slate-800 px-4 py-1.5 text-center shrink-0">
        <p className="text-slate-500 text-[11px] font-medium tracking-wide">
          Demo — Construtora Horizonte (dados simulados)
        </p>
      </div>

      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
