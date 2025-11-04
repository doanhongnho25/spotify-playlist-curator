import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, RefreshCw, Trash2, Wand2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { useToast } from "@/context/ToastContext";
import { API_ROUTES } from "@/utils/apiRoutes";
import { apiFetch } from "@/hooks/useApi";
import { useAccountContext } from "@/context/AccountContext";
import { formatDate } from "@/utils/formatters";

interface AccountRecord {
  id: string;
  display_name: string;
  email?: string;
  playlists_count: number;
  status: string;
  token_expires_at?: string;
  prefix?: string;
}

interface AccountsResponse {
  accounts: AccountRecord[];
}

export const AccountsPage = () => {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const { setActiveAccount, activeAccount } = useAccountContext();
  const [prefixDrafts, setPrefixDrafts] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery<AccountsResponse>({
    queryKey: ["accounts", "list"],
    queryFn: async () => apiFetch<AccountsResponse>(API_ROUTES.accounts.list)
  });

  const connect = () => {
    window.location.href = `${API_ROUTES.accounts.connect}`;
  };

  const updatePrefix = useMutation({
    mutationFn: (payload: { account_id: string; prefix: string }) =>
      apiFetch(API_ROUTES.accounts.prefix, {
        method: "POST",
        json: payload
      }),
    onSuccess: () => {
      addToast({ title: "Prefix updated", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["accounts", "list"] });
    },
    onError: (error) => {
      addToast({
        title: "Unable to update prefix",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const removeAccount = useMutation({
    mutationFn: (accountId: string) =>
      apiFetch(API_ROUTES.accounts.remove(accountId), { method: "POST" }),
    onSuccess: () => {
      addToast({ title: "Account removed", variant: "success" });
      queryClient.invalidateQueries({ queryKey: ["accounts", "list"] });
    },
    onError: (error) => {
      addToast({
        title: "Failed to remove account",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const refreshAccount = useMutation({
    mutationFn: (accountId: string) =>
      apiFetch(API_ROUTES.accounts.refresh(accountId), { method: "POST" }),
    onSuccess: () => {
      addToast({ title: "Token refresh queued", variant: "success" });
    },
    onError: (error) => {
      addToast({
        title: "Failed to refresh token",
        description: error instanceof Error ? error.message : "",
        variant: "error"
      });
    }
  });

  const handlePrefixSubmit = (event: FormEvent<HTMLFormElement>, account: AccountRecord) => {
    event.preventDefault();
    const prefix = prefixDrafts[account.id] ?? account.prefix ?? "";
    updatePrefix.mutate({ account_id: account.id, prefix });
  };

  return (
    <div className="space-y-6">
      <Card
        actions={
          <Button onClick={connect} type="button">
            <ExternalLink className="h-4 w-4" />
            Connect Spotify
          </Button>
        }
        title="Accounts"
      >
        <p className="text-sm text-white/60">
          Manage connected Spotify profiles, adjust naming prefixes, and monitor token health.
        </p>
      </Card>

      <div className="grid gap-4">
        {isLoading && <p className="text-white/60">Loading accounts…</p>}
        {!isLoading && data?.accounts.length === 0 && (
          <p className="text-white/60">No accounts connected yet.</p>
        )}
        {data?.accounts.map((account) => (
          <Card key={account.id}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-white">{account.display_name}</h3>
                <p className="text-sm text-white/60">
                  {account.email ?? "No email"} • {account.status} • Token expires {formatDate(account.token_expires_at)}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  onClick={() => setActiveAccount(account.id)}
                  variant={activeAccount?.id === account.id ? "primary" : "secondary"}
                >
                  <Wand2 className="h-4 w-4" />
                  Set active
                </Button>
                <Button
                  onClick={() => refreshAccount.mutate(account.id)}
                  variant="secondary"
                >
                  <RefreshCw className="h-4 w-4" />
                  Refresh token
                </Button>
                <Button
                  onClick={() => removeAccount.mutate(account.id)}
                  variant="danger"
                >
                  <Trash2 className="h-4 w-4" />
                  Remove
                </Button>
              </div>
            </div>
            <form
              className="mt-4 flex flex-col gap-3 md:flex-row md:items-end"
              onSubmit={(event) => handlePrefixSubmit(event, account)}
            >
              <div className="flex-1 space-y-2">
                <Label htmlFor={`prefix-${account.id}`}>Playlist prefix</Label>
                <Input
                  id={`prefix-${account.id}`}
                  onChange={(event) =>
                    setPrefixDrafts((prev) => ({ ...prev, [account.id]: event.target.value }))
                  }
                  placeholder="Vibe Collection"
                  value={prefixDrafts[account.id] ?? account.prefix ?? ""}
                />
              </div>
              <Button className="md:w-auto" type="submit" variant="secondary">
                Save prefix
              </Button>
              <div className="text-xs text-white/50">{account.playlists_count} playlists managed</div>
            </form>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AccountsPage;
