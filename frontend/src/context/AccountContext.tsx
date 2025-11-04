import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type PropsWithChildren
} from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";

export interface AccountSummary {
  id: string;
  display_name: string;
  email?: string;
  prefix?: string;
  status: string;
  playlists_count?: number;
  token_expires_at?: string;
}

interface ActiveAccountResponse {
  account?: AccountSummary | null;
}

interface AccountContextValue {
  activeAccount?: AccountSummary | null;
  setActiveAccount: (accountId: string) => Promise<void>;
  refresh: () => Promise<void>;
}

const AccountContext =
  createContext<AccountContextValue | undefined>(undefined);

export const AccountProvider = ({ children }: PropsWithChildren) => {
  const { isAuthenticated } = useAuth();

  const activeQuery = useQuery<ActiveAccountResponse>({
    queryKey: ["accounts", "active"],
    enabled: isAuthenticated,
    queryFn: async () => {
      if (!isAuthenticated) return { account: null };
      try {
        return await apiFetch<ActiveAccountResponse>(API_ROUTES.accounts.active);
      } catch (error) {
        console.warn("Failed to load active account", error);
        return { account: null };
      }
    }
  });

  const setActiveAccount = useCallback(
    async (accountId: string) => {
      await apiFetch(API_ROUTES.accounts.setActive, {
        method: "POST",
        json: { account_id: accountId }
      });
      await activeQuery.refetch();
    },
    [activeQuery]
  );

  const refresh = useCallback(async () => {
    await activeQuery.refetch();
  }, [activeQuery]);

  const value = useMemo<AccountContextValue>(
    () => ({
      activeAccount: activeQuery.data?.account,
      setActiveAccount,
      refresh
    }),
    [activeQuery.data?.account, refresh, setActiveAccount]
  );

  return <AccountContext.Provider value={value}>{children}</AccountContext.Provider>;
};

export const useAccountContext = () => {
  const context = useContext(AccountContext);
  if (!context) {
    throw new Error("useAccountContext must be used within an AccountProvider");
  }
  return context;
};
