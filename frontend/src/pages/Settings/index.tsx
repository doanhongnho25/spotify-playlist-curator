import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Button } from "@/components/ui/Button";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { useToast } from "@/context/ToastContext";

interface SettingsResponse {
  playlist_size: number;
  reshuffle_interval_days: number;
  cooldown_days: number;
  max_playlists_per_account: number;
  artist_cap: number;
  default_prefix: string;
}

export const SettingsPage = () => {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const { data } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: async () => apiFetch<SettingsResponse>(API_ROUTES.settings.root)
  });

  const [formState, setFormState] = useState<SettingsResponse | null>(null);

  useEffect(() => {
    if (data) {
      setFormState(data);
    }
  }, [data]);

  const mutation = useMutation({
    mutationFn: (payload: SettingsResponse) =>
      apiFetch(API_ROUTES.settings.root, {
        method: "POST",
        json: payload
      }),
    onSuccess: () => {
      addToast({ title: "Settings saved", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
    onError: (error) => {
      addToast({
        title: "Failed to save settings",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formState) return;
    mutation.mutate(formState);
  };

  const handleChange = (field: keyof SettingsResponse, value: string) => {
    setFormState((prev) =>
      prev
        ? {
            ...prev,
            [field]: field === "default_prefix" ? value : Number(value)
          }
        : prev
    );
  };

  const restoreDefaults = () => {
    if (!data) return;
    setFormState(data);
  };

  return (
    <div className="space-y-6">
      <Card title="System configuration">
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <Label htmlFor="playlist-size">Playlist size</Label>
            <Input
              id="playlist-size"
              min={1}
              onChange={(event) => handleChange("playlist_size", event.target.value)}
              type="number"
              value={formState?.playlist_size ?? ""}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="reshuffle-interval">Reshuffle interval (days)</Label>
            <Input
              id="reshuffle-interval"
              min={1}
              onChange={(event) => handleChange("reshuffle_interval_days", event.target.value)}
              type="number"
              value={formState?.reshuffle_interval_days ?? ""}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="cooldown">Cooldown (days)</Label>
            <Input
              id="cooldown"
              min={1}
              onChange={(event) => handleChange("cooldown_days", event.target.value)}
              type="number"
              value={formState?.cooldown_days ?? ""}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="max-playlists">Max playlists per account</Label>
            <Input
              id="max-playlists"
              min={1}
              onChange={(event) => handleChange("max_playlists_per_account", event.target.value)}
              type="number"
              value={formState?.max_playlists_per_account ?? ""}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="artist-cap">Artist cap per playlist</Label>
            <Input
              id="artist-cap"
              min={1}
              onChange={(event) => handleChange("artist_cap", event.target.value)}
              type="number"
              value={formState?.artist_cap ?? ""}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="default-prefix">Default prefix</Label>
            <Input
              id="default-prefix"
              onChange={(event) => handleChange("default_prefix", event.target.value)}
              placeholder="Vibe Collection"
              value={formState?.default_prefix ?? ""}
            />
          </div>
          <div className="md:col-span-2 flex flex-wrap gap-3">
            <Button disabled={mutation.isPending} type="submit">
              {mutation.isPending ? "Saving…" : "Save changes"}
            </Button>
            <Button onClick={restoreDefaults} type="button" variant="secondary">
              Restore default
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default SettingsPage;
