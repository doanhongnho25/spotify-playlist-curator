import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { formatNumber } from "@/utils/formatters";
import { useToast } from "@/context/ToastContext";

interface OverviewMetrics {
  stats?: {
    accounts_connected?: number;
    playlists_active?: number;
    tracks_total?: number;
    tracks_usable?: number;
    next_reshuffle_in_days?: number;
    last_sync_at?: string;
  };
  playlist_growth?: Array<{ date: string; value: number }>;
  reshuffle_volume?: Array<{ week: string; value: number }>;
  account_load?: Array<{ name: string; value: number }>;
  top_artists?: Array<{ artist: string; plays: number }>;
}

const COLORS = ["#6A5AE0", "#A85CF9", "#3CC2FF", "#4ADE80", "#FACC15"];

export const DashboardPage = () => {
  const { addToast } = useToast();
  const { data } = useQuery<OverviewMetrics>({
    queryKey: ["metrics", "overview", "dashboard"],
    queryFn: async () => apiFetch<OverviewMetrics>(API_ROUTES.metrics.overview),
    refetchInterval: 30_000
  });

  const playlistGrowth = useMemo(
    () => data?.playlist_growth ?? [],
    [data?.playlist_growth]
  );

  const reshuffleVolume = useMemo(
    () => data?.reshuffle_volume ?? [],
    [data?.reshuffle_volume]
  );

  const accountLoad = useMemo(
    () => data?.account_load ?? [],
    [data?.account_load]
  );

  const topArtists = useMemo(
    () => data?.top_artists ?? [],
    [data?.top_artists]
  );

  const triggerAction = (label: string) => {
    addToast({ title: `${label} queued`, description: "The request will run shortly.", variant: "success" });
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <Card title="Accounts connected">
          <p className="text-3xl font-semibold text-white">
            {formatNumber(data?.stats?.accounts_connected)}
          </p>
        </Card>
        <Card title="Playlists active">
          <p className="text-3xl font-semibold text-white">
            {formatNumber(data?.stats?.playlists_active)}
          </p>
        </Card>
        <Card title="Tracks usable">
          <p className="text-3xl font-semibold text-white">
            {formatNumber(data?.stats?.tracks_usable ?? data?.stats?.tracks_total)}
          </p>
        </Card>
        <Card title="Next reshuffle">
          <p className="text-3xl font-semibold text-white">
            {data?.stats?.next_reshuffle_in_days ?? "—"} days
          </p>
        </Card>
        <Card title="Last sync">
          <p className="text-3xl font-semibold text-white">
            {data?.stats?.last_sync_at
              ? new Date(data.stats.last_sync_at).toLocaleString()
              : "—"}
          </p>
        </Card>
        <Card title="Track pool">
          <p className="text-3xl font-semibold text-white">
            {formatNumber(data?.stats?.tracks_total)} total
          </p>
        </Card>
      </div>

      <Card
        actions={
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => triggerAction("Create playlists")}>Create playlists</Button>
            <Button onClick={() => triggerAction("Reshuffle all")}>Reshuffle all</Button>
            <Button onClick={() => triggerAction("Export catalog")} variant="secondary">
              Export playlist list
            </Button>
          </div>
        }
        title="Operations"
      >
        <p className="text-sm text-white/60">
          Access the quick commands to provision new playlists, force a reshuffle, or export the public index.
        </p>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Playlist growth">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={playlistGrowth}>
                <CartesianGrid opacity={0.1} stroke="#444" strokeDasharray="4 8" />
                <XAxis dataKey="date" stroke="#999" tickLine={false} />
                <YAxis stroke="#999" tickLine={false} />
                <Tooltip cursor={{ stroke: "#A85CF9", strokeWidth: 1 }} />
                <Line dataKey="value" stroke="#A85CF9" strokeWidth={3} type="monotone" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="Reshuffle volume">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={reshuffleVolume}>
                <CartesianGrid opacity={0.1} stroke="#444" strokeDasharray="4 8" />
                <XAxis dataKey="week" stroke="#999" tickLine={false} />
                <YAxis stroke="#999" tickLine={false} />
                <Tooltip cursor={{ fill: "rgba(168,92,249,0.15)" }} />
                <Bar dataKey="value" fill="#6A5AE0" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Account load">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={accountLoad}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={4}
                >
                  {accountLoad.map((entry, index) => (
                    <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="Top artists">
          <div className="space-y-3">
            {topArtists.map((artist) => (
              <div
                className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3"
                key={artist.artist}
              >
                <p className="font-medium text-white">{artist.artist}</p>
                <span className="text-sm text-white/60">{formatNumber(artist.plays)} plays</span>
              </div>
            ))}
            {topArtists.length === 0 && (
              <p className="text-sm text-white/50">No artist data available yet.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
