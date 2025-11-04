import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "@/hooks/useAuth";
import { AccountProvider } from "@/context/AccountContext";
import { ToastProvider } from "@/context/ToastContext";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/pages/Dashboard";
import { AccountsPage } from "@/pages/Accounts";
import { PlaylistsPage } from "@/pages/Playlists";
import { LibraryPage } from "@/pages/Library";
import { SettingsPage } from "@/pages/Settings";
import { AutomationPage } from "@/pages/Automation";
import { AssistantPage } from "@/pages/Assistant";
import { LoginPage } from "@/pages/Login";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#121212] text-white">
        Loading dashboard…
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return <>{children}</>;
};

const Router = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route
      element={
        <ProtectedRoute>
          <AppShell />
        </ProtectedRoute>
      }
      path="/"
    >
      <Route index element={<Navigate replace to="/dashboard" />} />
      <Route path="dashboard" element={<DashboardPage />} />
      <Route path="accounts" element={<AccountsPage />} />
      <Route path="playlists" element={<PlaylistsPage />} />
      <Route path="library" element={<LibraryPage />} />
      <Route path="settings" element={<SettingsPage />} />
      <Route path="automation" element={<AutomationPage />} />
      <Route path="assistant" element={<AssistantPage />} />
    </Route>
    <Route path="*" element={<Navigate replace to="/dashboard" />} />
  </Routes>
);

const App = () => (
  <AuthProvider>
    <ToastProvider>
      <AccountProvider>
        <BrowserRouter>
          <Router />
        </BrowserRouter>
      </AccountProvider>
    </ToastProvider>
  </AuthProvider>
);

export default App;
