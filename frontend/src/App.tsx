import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import Recommendations from "./pages/Recommendations";
import Alerts from "./pages/Alerts";
import Data from "./pages/Data";
import Admin from "./pages/Admin";

function AppContent() {
  return (
    <Layout>
      {(activePage) => {
        switch (activePage) {
          case "dashboard":
            return <Dashboard />;
          case "recommendations":
            return <Recommendations />;
          case "alerts":
            return <Alerts />;
          case "data":
            return <Data />;
          case "admin":
            return <Admin />;
          default:
            return <Dashboard />;
        }
      }}
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppContent />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
