import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown } from "lucide-react";
import { useAccountContext } from "@/context/AccountContext";
import { apiFetch } from "@/hooks/useApi";
import { useAuth } from "@/hooks/useAuth";
import { API_ROUTES } from "@/utils/apiRoutes";
import { STATUS_BADGES } from "@/utils/constants";

interface MetricsOverview {
  status?: keyof typeof STATUS_BADGES;
  next_reshuffle_in_days?: number;
}

interface AccountsListResponse {
  accounts: Array<{
    id: string;
    display_name: string;
    prefix?: string;
    status: string;
  }>;
}

export const Navbar = () => {
  const { activeAccount, setActiveAccount } = useAccountContext();
  const { isAuthenticated, user } = useAuth();

  const { data: accounts } = useQuery<AccountsListResponse>({
    queryKey: ["accounts", "list"],
    enabled: isAuthenticated,
    queryFn: async () => apiFetch<AccountsListResponse>(API_ROUTES.accounts.list)
  });

  const { data: overview } = useQuery<MetricsOverview>({
    queryKey: ["metrics", "overview"],
    enabled: isAuthenticated,
    queryFn: async () => apiFetch<MetricsOverview>(API_ROUTES.metrics.overview),
    refetchInterval: 30_000
  });

  const badge = useMemo(() => {
    if (overview?.status && STATUS_BADGES[overview.status]) {
      return STATUS_BADGES[overview.status];
    }
    return STATUS_BADGES.healthy;
  }, [overview?.status]);

  return (
    <header className="flex h-20 items-center justify-between border-b border-white/10 bg-black/30 px-6 backdrop-blur-lg">
      <div className="flex items-center gap-3 text-sm">
        <span className="text-lg">{badge.icon}</span>
        <div>
          <p className="text-sm font-semibold text-white">{badge.label}</p>
          <p className="text-xs text-white/60">
            Next reshuffle in {overview?.next_reshuffle_in_days ?? "—"} days
          </p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-wide text-white/50">
            Active account
          </span>
          <div className="relative">
            <select
              className="appearance-none rounded-xl border border-white/20 bg-white/10 px-4 py-2 pr-8 text-sm text-white focus:border-accent focus:outline-none"
              onChange={(event) => setActiveAccount(event.target.value)}
              value={activeAccount?.id ?? ""}
            >
              <option value="" disabled>
                Select account
              </option>
              {accounts?.accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.display_name}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-white/50" />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-accent to-accent-soft text-center text-base font-semibold leading-10">
            {user?.username?.[0]?.toUpperCase() ?? "A"}
          </div>
          <div className="text-xs">
            <p className="font-semibold text-white">{user?.username ?? "admin"}</p>
            <p className="text-white/50">Dashboard access</p>
          </div>
        </div>
      </div>
    </header>
  );
};
