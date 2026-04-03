import { createContext, useContext, useState, type ReactNode } from "react";
import { mockLogin } from "../api/mockApi";
import { safeStorage } from "../lib/storage";

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
  safeStorage.removeItem("picnep_token");
  safeStorage.removeItem("picnep_user");
  return null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(getInitialUser);
  const [isLoading] = useState(false);

  const login = async (email: string, password: string): Promise<boolean> => {
    const data = await mockLogin(email, password);
    if (!data) return false;

    safeStorage.setItem("picnep_token", data.access_token);
    const authUser: AuthUser = { name: data.name, role: data.role, email };
    setUser(authUser);
    safeStorage.setItem("picnep_user", JSON.stringify(authUser));
    return true;
  };

  const logout = () => {
    safeStorage.removeItem("picnep_token");
    safeStorage.removeItem("picnep_user");
    setUser(null);
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
