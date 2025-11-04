import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { formatDate, formatNumber } from "@/utils/formatters";
import { Label } from "@/components/ui/Label";

interface AlbumRecord {
  id: string;
  name: string;
  artist: string;
  tracks_count: number;
  popularity?: number;
  added_at?: string;
  usable?: boolean;
}

interface AlbumResponse {
  albums: AlbumRecord[];
}

interface TrackRecord {
  id: string;
  name: string;
  artist: string;
  popularity?: number;
  energy?: number;
  danceability?: number;
  tempo?: number;
  last_used_at?: string;
  usable?: boolean;
}

interface TracksResponse {
  tracks: TrackRecord[];
}

export const LibraryPage = () => {
  const [search, setSearch] = useState("");
  const [onlyUsable, setOnlyUsable] = useState(true);
  const [selectedAlbum, setSelectedAlbum] = useState<string | null>(null);

  const { data: albumsData } = useQuery<AlbumResponse>({
    queryKey: ["library", "albums", { search, onlyUsable }],
    queryFn: async () =>
      apiFetch<AlbumResponse>(
        `${API_ROUTES.library.albums}?query=${encodeURIComponent(search)}&usable=${onlyUsable}`
      )
  });

  const { data: tracksData } = useQuery<TracksResponse>({
    queryKey: ["library", "tracks", selectedAlbum],
    enabled: Boolean(selectedAlbum),
    queryFn: async () =>
      apiFetch<TracksResponse>(
        `${API_ROUTES.library.tracks}?album_id=${encodeURIComponent(selectedAlbum ?? "")}`
      )
  });

  const albums = useMemo(() => albumsData?.albums ?? [], [albumsData?.albums]);
  const tracks = useMemo(() => tracksData?.tracks ?? [], [tracksData?.tracks]);

  return (
    <div className="space-y-6">
      <Card title="Music library">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="album-search">Search albums or artists</Label>
            <Input
              id="album-search"
              onChange={(event) => setSearch(event.target.value)}
              placeholder="e.g. midnight, aurora"
              value={search}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="usable-filter">Show usable only</Label>
            <input
              checked={onlyUsable}
              className="h-4 w-4 rounded border-white/30 bg-transparent"
              id="usable-filter"
              onChange={(event) => setOnlyUsable(event.target.checked)}
              type="checkbox"
            />
          </div>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <Card title="Albums">
          <div className="overflow-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="text-white/60">
                  <th className="py-2">Album</th>
                  <th className="py-2">Artist</th>
                  <th className="py-2">Tracks</th>
                  <th className="py-2">Popularity</th>
                  <th className="py-2">Added</th>
                </tr>
              </thead>
              <tbody>
                {albums.map((album) => (
                  <tr
                    className={`cursor-pointer border-t border-white/10 transition hover:bg-white/5 ${
                      selectedAlbum === album.id ? "bg-white/10" : ""
                    }`}
                    key={album.id}
                    onClick={() => setSelectedAlbum(album.id)}
                  >
                    <td className="py-2 font-medium text-white">{album.name}</td>
                    <td className="py-2 text-white/60">{album.artist}</td>
                    <td className="py-2 text-white/60">{formatNumber(album.tracks_count)}</td>
                    <td className="py-2 text-white/60">{album.popularity ?? "—"}</td>
                    <td className="py-2 text-white/60">{formatDate(album.added_at)}</td>
                  </tr>
                ))}
                {albums.length === 0 && (
                  <tr>
                    <td className="py-6 text-center text-white/50" colSpan={5}>
                      No albums found. Adjust your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card
          description="Select an album to view its tracks and audio features."
          title="Tracks"
        >
          {tracks.length === 0 ? (
            <p className="text-sm text-white/60">No tracks loaded.</p>
          ) : (
            <div className="space-y-3">
              {tracks.map((track) => (
                <div className="rounded-xl border border-white/10 p-3" key={track.id}>
                  <p className="font-medium text-white">{track.name}</p>
                  <p className="text-xs text-white/60">{track.artist}</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-white/50">
                    <span>Popularity: {track.popularity ?? "—"}</span>
                    <span>Energy: {track.energy?.toFixed(2) ?? "—"}</span>
                    <span>Danceability: {track.danceability?.toFixed(2) ?? "—"}</span>
                    <span>Tempo: {track.tempo?.toFixed(0) ?? "—"} BPM</span>
                    <span>Last used: {formatDate(track.last_used_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default LibraryPage;
