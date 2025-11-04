import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type PropsWithChildren
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";

interface DevStatus {
  authenticated: boolean;
  user?: {
    username: string;
  };
}

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  user?: DevStatus["user"];
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: PropsWithChildren) => {
  const queryClient = useQueryClient();

  const statusQuery = useQuery<DevStatus>({
    queryKey: ["auth", "status"],
    queryFn: async () => {
      try {
        return await apiFetch<DevStatus>(API_ROUTES.auth.status, {
          method: "GET"
        });
      } catch (error) {
        console.warn("Failed to fetch auth status", error);
        return { authenticated: false };
      }
    },
    staleTime: 15_000
  });

  const refresh = useCallback(async () => {
    await statusQuery.refetch();
  }, [statusQuery]);

  const login = useCallback(
    async (username: string, password: string) => {
      await apiFetch(API_ROUTES.auth.login, {
        method: "POST",
        json: { username, password }
      });
      await statusQuery.refetch();
      await queryClient.invalidateQueries();
    },
    [queryClient, statusQuery]
  );

  const logout = useCallback(async () => {
    await apiFetch(API_ROUTES.auth.logout, { method: "POST" });
    await statusQuery.refetch();
    queryClient.clear();
  }, [queryClient, statusQuery]);

  const value = useMemo<AuthContextValue>(() => {
    const authenticated = Boolean(statusQuery.data?.authenticated);
    return {
      isAuthenticated: authenticated,
      isLoading: statusQuery.isLoading,
      user: statusQuery.data?.user,
      login,
      logout,
      refresh
    };
  }, [login, logout, refresh, statusQuery.data, statusQuery.isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
