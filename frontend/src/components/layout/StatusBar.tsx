import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/hooks/useApi";
import { useAuth } from "@/hooks/useAuth";
import { API_ROUTES } from "@/utils/apiRoutes";
import { formatNumber } from "@/utils/formatters";

interface StatusSnapshot {
  albums_total?: number;
  tracks_usable?: number;
  playlists_active?: number;
  accounts_connected?: number;
  last_sync_at?: string;
}

export const StatusBar = () => {
  const { isAuthenticated } = useAuth();

  const { data } = useQuery<StatusSnapshot>({
    queryKey: ["metrics", "status-bar"],
    enabled: isAuthenticated,
    queryFn: async () => apiFetch<StatusSnapshot>(API_ROUTES.metrics.overview),
    refetchInterval: 30_000
  });

  return (
    <section className="grid grid-cols-2 gap-4 border-b border-white/10 bg-black/20 px-6 py-4 text-xs sm:grid-cols-4 lg:grid-cols-5">
      <div>
        <p className="text-white/50">Accounts</p>
        <p className="text-sm font-semibold text-white">
          {formatNumber(data?.accounts_connected)}
        </p>
      </div>
      <div>
        <p className="text-white/50">Playlists</p>
        <p className="text-sm font-semibold text-white">
          {formatNumber(data?.playlists_active)}
        </p>
      </div>
      <div>
        <p className="text-white/50">Tracks usable</p>
        <p className="text-sm font-semibold text-white">
          {formatNumber(data?.tracks_usable)}
        </p>
      </div>
      <div>
        <p className="text-white/50">Albums</p>
        <p className="text-sm font-semibold text-white">
          {formatNumber(data?.albums_total)}
        </p>
      </div>
      <div className="hidden lg:block">
        <p className="text-white/50">Last sync</p>
        <p className="text-sm font-semibold text-white">
          {data?.last_sync_at ? new Date(data.last_sync_at).toLocaleString() : "—"}
        </p>
      </div>
    </section>
  );
};
