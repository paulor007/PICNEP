import { useState } from "react";
import Sidebar from "./Sidebar";

interface LayoutProps {
  children: (activePage: string) => React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [activePage, setActivePage] = useState("dashboard");

  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar active={activePage} onNavigate={setActivePage} />
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children(activePage)}</div>
      </main>
    </div>
  );
}
