import React, { useState, useEffect, useMemo } from 'react';
import { LogOut, LogIn, RefreshCcw, PlusCircle, Trash2 } from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'accounts', label: 'Accounts' },
  { id: 'albums', label: 'Albums' },
  { id: 'policies', label: 'Policies & Playlists' },
  { id: 'manager', label: 'Manager' },
  { id: 'metrics', label: 'Metrics' },
];

function TextInput({ label, type = 'text', value, onChange }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-slate-200">{label}</span>
      <input
        type={type}
        value={value}
        onChange={onChange}
        className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring focus:ring-indigo-500/40"
      />
    </label>
  );
}

function SectionCard({ title, children, actions }) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-inner shadow-black/30">
      <header className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </header>
      <div className="text-slate-200">{children}</div>
    </section>
  );
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [authError, setAuthError] = useState('');
  const [accounts, setAccounts] = useState([]);
  const [activeAccountId, setActiveAccountId] = useState(null);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [accountActionMessage, setAccountActionMessage] = useState('');

  useEffect(() => {
    checkAuthStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAccounts();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const accountOptions = useMemo(
    () =>
      accounts
        .filter((acct) => acct.status === 'active')
        .map((acct) => ({
          value: acct.id,
          label: acct.display_name || acct.spotify_user_id,
        })),
    [accounts]
  );

  async function checkAuthStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/dev-status`, {
        credentials: 'include',
      });
      if (!res.ok) {
        setIsAuthenticated(false);
        return;
      }
      const data = await res.json();
      setIsAuthenticated(data.authenticated);
      setActiveAccountId(data.active_account_id || null);
    } catch (error) {
      console.error('Failed to check auth status', error);
      setIsAuthenticated(false);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/dev-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const error = await res.json();
        setAuthError(error.detail || 'Invalid credentials');
        return;
      }
      setIsAuthenticated(true);
      setActiveTab('overview');
      await fetchAccounts();
    } catch (error) {
      console.error('Login failed', error);
      setAuthError('Unable to login. Please try again.');
    }
  }

  async function handleLogout() {
    try {
      await fetch(`${API_BASE}/api/v1/auth/dev-logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout failed', error);
    }
    setIsAuthenticated(false);
    setAccounts([]);
    setActiveAccountId(null);
  }

  async function fetchAccounts() {
    setLoadingAccounts(true);
    setAccountActionMessage('');
    try {
      const res = await fetch(`${API_BASE}/api/v1/accounts/list`, {
        credentials: 'include',
      });
      if (!res.ok) {
        throw new Error('Unable to load accounts');
      }
      const data = await res.json();
      setAccounts(data.accounts || []);
      setActiveAccountId(data.active_account_id || null);
    } catch (error) {
      console.error(error);
      setAccountActionMessage('Failed to load accounts');
    } finally {
      setLoadingAccounts(false);
    }
  }

  async function handleSetActiveAccount(value) {
    const accountId = value || null;
    try {
      const res = await fetch(`${API_BASE}/api/v1/accounts/active/set`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ account_id: accountId }),
      });
      if (!res.ok) {
        throw new Error('Unable to set active account');
      }
      const data = await res.json();
      setActiveAccountId(data.active_account_id || null);
      setAccountActionMessage('Active account updated');
    } catch (error) {
      console.error(error);
      setAccountActionMessage('Failed to update active account');
    }
  }

  async function handleRemoveAccount(accountId) {
    if (!window.confirm('Remove this Spotify account?')) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/accounts/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ account_id: accountId }),
      });
      if (!res.ok) {
        throw new Error('Unable to remove account');
      }
      await fetchAccounts();
      setAccountActionMessage('Account removed');
    } catch (error) {
      console.error(error);
      setAccountActionMessage('Failed to remove account');
    }
  }

  async function handleConnectSpotify() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/oauth/spotify/connect`, {
        credentials: 'include',
      });
      if (!res.ok) {
        throw new Error('Unable to begin Spotify OAuth');
      }
      const data = await res.json();
      window.location.href = data.authorize_url;
    } catch (error) {
      console.error(error);
      setAccountActionMessage('Failed to initiate Spotify OAuth');
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-black/40">
          <h1 className="mb-6 text-center text-2xl font-bold text-white">Vibe Control Center</h1>
          <p className="mb-6 text-center text-sm text-slate-400">
            Sign in with the development dashboard credentials to access the unified operations console.
          </p>
          <form className="space-y-4" onSubmit={handleLogin}>
            <TextInput label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
            <TextInput label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {authError && <p className="text-sm text-rose-400">{authError}</p>}
            <button
              type="submit"
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-500 px-4 py-2 font-semibold text-white transition hover:bg-indigo-400"
            >
              <LogIn className="h-4 w-4" />
              Sign In
            </button>
          </form>
          <p className="mt-6 text-center text-xs text-slate-500">Default credentials: admin / admin</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Vibe Control Center</h1>
            <p className="text-sm text-slate-400">Ingest • Curate • Sync • Scale</p>
          </div>
          <div className="flex items-center gap-4">
            <div>
              <label className="text-xs uppercase tracking-wide text-slate-400">Active Account</label>
              <select
                className="mt-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                value={activeAccountId || ''}
                onChange={(e) => handleSetActiveAccount(e.target.value || null)}
              >
                <option value="">No active account</option>
                {accountOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-rose-500 hover:text-rose-300"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-8">
        <nav className="flex flex-wrap gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                activeTab === tab.id
                  ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/30'
                  : 'border border-slate-700 text-slate-300 hover:border-slate-500'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {activeTab === 'overview' && (
          <SectionCard title="System Snapshot">
            <p className="text-sm text-slate-300">
              Welcome to the unified dashboard. Connect Spotify accounts, ingest album sources, manage policies, and oversee daily
              automation waves from a single interface.
            </p>
          </SectionCard>
        )}

        {activeTab === 'accounts' && (
          <SectionCard
            title="Spotify Accounts"
            actions={
              <button
                onClick={handleConnectSpotify}
                className="flex items-center gap-2 rounded-lg bg-emerald-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-400"
              >
                <PlusCircle className="h-4 w-4" /> Connect Account
              </button>
            }
          >
            <div className="space-y-4">
              {accountActionMessage && <p className="text-sm text-slate-400">{accountActionMessage}</p>}
              {loadingAccounts ? (
                <p className="text-sm text-slate-400">Loading accounts…</p>
              ) : accounts.length === 0 ? (
                <p className="text-sm text-slate-400">No Spotify accounts connected yet.</p>
              ) : (
                <ul className="divide-y divide-slate-800 border border-slate-800/60">
                  {accounts.map((account) => (
                    <li key={account.id} className="flex items-center justify-between gap-4 p-4">
                      <div>
                        <p className="font-medium text-white">{account.display_name || account.spotify_user_id}</p>
                        <p className="text-xs text-slate-400">Status: {account.status}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">
                          Expires {account.expires_at ? new Date(account.expires_at).toLocaleString() : 'N/A'}
                        </span>
                        <button
                          onClick={() => handleRemoveAccount(account.id)}
                          className="rounded-lg border border-rose-700 px-3 py-2 text-xs font-semibold text-rose-300 transition hover:bg-rose-500/10"
                        >
                          <Trash2 className="mr-1 inline h-3 w-3" /> Remove
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
              <button
                onClick={fetchAccounts}
                className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-indigo-400 hover:text-indigo-200"
              >
                <RefreshCcw className="h-4 w-4" /> Refresh
              </button>
            </div>
          </SectionCard>
        )}

        {activeTab === 'albums' && (
          <SectionCard title="Album Ingest">
            <p className="text-sm text-slate-300">
              Paste album URLs to validate and queue ingest jobs. Progress tracking and worker orchestration controls will appear
              here in the next iteration.
            </p>
          </SectionCard>
        )}

        {activeTab === 'policies' && (
          <SectionCard title="Policies & Playlists">
            <p className="text-sm text-slate-300">
              Manage curation policies, create playlist templates, and trigger manual syncs to the active Spotify account.
            </p>
          </SectionCard>
        )}

        {activeTab === 'manager' && (
          <SectionCard title="Scaling Manager">
            <p className="text-sm text-slate-300">
              Review projected playlist counts, compute scaling plans, and execute rebalance operations across Spotify accounts.
            </p>
          </SectionCard>
        )}

        {activeTab === 'metrics' && (
          <SectionCard title="Metrics & Health">
            <p className="text-sm text-slate-300">
              Observability panels will surface ingest throughput, playlist sync volume, rate-limit incidents, and account health
              status.
            </p>
          </SectionCard>
        )}
      </main>
    </div>
  );
}
