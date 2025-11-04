import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { useToast } from "@/context/ToastContext";
import { formatDate, formatRelativeDays } from "@/utils/formatters";

interface PlaylistRecord {
  id: string;
  name: string;
  account_display_name: string;
  size: number;
  last_reshuffle_at?: string;
  next_reshuffle_at?: string;
  status: string;
  spotify_url?: string;
}

interface PlaylistsResponse {
  playlists: PlaylistRecord[];
}

export const PlaylistsPage = () => {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [createPayload, setCreatePayload] = useState({
    account_id: "",
    count: 10,
    prefix: "",
    interval_days: 5
  });

  const { data } = useQuery<PlaylistsResponse>({
    queryKey: ["playlists", "list"],
    queryFn: async () => apiFetch<PlaylistsResponse>(API_ROUTES.playlists.list)
  });

  const playlists = useMemo(() => data?.playlists ?? [], [data?.playlists]);

  const toggleAll = (value: boolean) => {
    const mapping: Record<string, boolean> = {};
    playlists.forEach((playlist) => {
      mapping[playlist.id] = value;
    });
    setSelected(mapping);
  };

  const toggleOne = (id: string) => {
    setSelected((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const selectedIds = useMemo(
    () => Object.entries(selected).filter(([, value]) => value).map(([key]) => key),
    [selected]
  );

  const createPlaylists = useMutation({
    mutationFn: () =>
      apiFetch(API_ROUTES.playlists.create, {
        method: "POST",
        json: createPayload
      }),
    onSuccess: () => {
      addToast({ title: "Playlists queued", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["playlists", "list"] });
    },
    onError: (error) => {
      addToast({
        title: "Failed to create playlists",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const reshuffle = useMutation({
    mutationFn: (payload: { playlist_ids?: string[]; mode?: string }) =>
      apiFetch(API_ROUTES.playlists.reshuffleBulk, {
        method: "POST",
        json: payload
      }),
    onSuccess: () => {
      addToast({ title: "Reshuffle queued", variant: "success" });
    },
    onError: (error) => {
      addToast({
        title: "Reshuffle failed",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const deletePlaylist = useMutation({
    mutationFn: (playlistId: string) =>
      apiFetch(API_ROUTES.playlists.delete(playlistId), { method: "DELETE" }),
    onSuccess: () => {
      addToast({ title: "Playlist removed", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["playlists", "list"] });
    },
    onError: (error) => {
      addToast({
        title: "Failed to delete playlist",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const handleCreate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    createPlaylists.mutate();
  };

  return (
    <div className="space-y-6">
      <Card title="Create playlists">
        <form className="grid gap-4 md:grid-cols-4" onSubmit={handleCreate}>
          <div className="space-y-2">
            <Label htmlFor="create-account">Account ID</Label>
            <Input
              id="create-account"
              onChange={(event) =>
                setCreatePayload((prev) => ({ ...prev, account_id: event.target.value }))
              }
              placeholder="account uuid"
              value={createPayload.account_id}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="create-count">Count</Label>
            <Input
              id="create-count"
              min={1}
              onChange={(event) =>
                setCreatePayload((prev) => ({ ...prev, count: Number(event.target.value) }))
              }
              type="number"
              value={createPayload.count}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="create-prefix">Prefix</Label>
            <Input
              id="create-prefix"
              onChange={(event) =>
                setCreatePayload((prev) => ({ ...prev, prefix: event.target.value }))
              }
              placeholder="Optional prefix"
              value={createPayload.prefix}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="create-interval">Reshuffle every (days)</Label>
            <Input
              id="create-interval"
              min={1}
              onChange={(event) =>
                setCreatePayload((prev) => ({ ...prev, interval_days: Number(event.target.value) }))
              }
              type="number"
              value={createPayload.interval_days}
            />
          </div>
          <Button className="md:col-span-4" disabled={createPlaylists.isPending} type="submit">
            {createPlaylists.isPending ? "Creating…" : "Create playlists"}
          </Button>
        </form>
      </Card>

      <Card
        actions={
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => reshuffle.mutate({ mode: "all" })} variant="secondary">
              Reshuffle all
            </Button>
            <Button
              disabled={selectedIds.length === 0}
              onClick={() => reshuffle.mutate({ playlist_ids: selectedIds })}
              variant="secondary"
            >
              Reshuffle selected
            </Button>
            <Button
              disabled={selectedIds.length === 0}
              onClick={() => {
                selectedIds.forEach((id) => deletePlaylist.mutate(id));
                setSelected({});
              }}
              variant="danger"
            >
              Delete selected
            </Button>
          </div>
        }
        title="Playlists"
      >
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="text-white/60">
                <th className="w-12 py-2">
                  <input
                    checked={selectedIds.length === playlists.length && playlists.length > 0}
                    className="h-4 w-4 rounded border-white/30 bg-transparent"
                    onChange={(event) => toggleAll(event.target.checked)}
                    type="checkbox"
                  />
                </th>
                <th className="py-2">Playlist</th>
                <th className="py-2">Account</th>
                <th className="py-2">Last reshuffle</th>
                <th className="py-2">Next</th>
                <th className="py-2">Size</th>
                <th className="py-2">Status</th>
                <th className="py-2">Link</th>
              </tr>
            </thead>
            <tbody>
              {playlists.map((playlist) => (
                <tr className="border-t border-white/10" key={playlist.id}>
                  <td className="py-3">
                    <input
                      checked={Boolean(selected[playlist.id])}
                      className="h-4 w-4 rounded border-white/30 bg-transparent"
                      onChange={() => toggleOne(playlist.id)}
                      type="checkbox"
                    />
                  </td>
                  <td className="py-3 font-medium text-white">{playlist.name}</td>
                  <td className="py-3 text-white/70">{playlist.account_display_name}</td>
                  <td className="py-3 text-white/60">{formatDate(playlist.last_reshuffle_at)}</td>
                  <td className="py-3 text-white/60">{formatRelativeDays(playlist.next_reshuffle_at)}</td>
                  <td className="py-3 text-white/60">{playlist.size}</td>
                  <td className="py-3 text-white/60">{playlist.status}</td>
                  <td className="py-3 text-white/60">
                    {playlist.spotify_url ? (
                      <a
                        className="text-accent-soft underline"
                        href={playlist.spotify_url}
                        rel="noreferrer"
                        target="_blank"
                      >
                        Open
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
              {playlists.length === 0 && (
                <tr>
                  <td className="py-6 text-center text-white/50" colSpan={8}>
                    No playlists to display.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default PlaylistsPage;
