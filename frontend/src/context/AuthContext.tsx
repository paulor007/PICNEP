import { createContext, useContext, useState, type ReactNode } from "react";
import { api } from "../api/client";

interface AuthUser {
  name: string;
  role: string;
  email: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function getInitialUser(): AuthUser | null {
  const saved = localStorage.getItem("picnep_user");
  const token = localStorage.getItem("picnep_token");
  if (saved && token) {
    return JSON.parse(saved);
  }
  return null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(getInitialUser);
  const [isLoading] = useState(false);

  const login = async (email: string, password: string): Promise<boolean> => {
    const data = await api.loginRequest(email, password);
    if (!data) return false;

    api.setToken(data.access_token);
    const authUser: AuthUser = { name: data.name, role: data.role, email };
    setUser(authUser);
    localStorage.setItem("picnep_user", JSON.stringify(authUser));
    return true;
  };

  const logout = () => {
    api.clearToken();
    setUser(null);
    localStorage.removeItem("picnep_user");
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
