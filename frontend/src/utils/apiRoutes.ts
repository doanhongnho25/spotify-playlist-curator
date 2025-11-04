export const API_ROUTES = {
  auth: {
    login: "/api/v1/auth/dev-login",
    status: "/api/v1/auth/dev-status",
    logout: "/api/v1/auth/dev-logout"
  },
  accounts: {
    list: "/api/v1/accounts/list",
    connect: "/api/v1/oauth/spotify/connect",
    remove: (id: string) => `/api/v1/accounts/${id}/remove`,
    refresh: (id: string) => `/api/v1/accounts/${id}/refresh`,
    setActive: "/api/v1/accounts/active/set",
    active: "/api/v1/accounts/active/get",
    prefix: "/api/v1/accounts/prefix"
  },
  ingest: {
    validate: "/api/v1/ingest/albums/validate",
    submit: "/api/v1/ingest/albums/submit",
    submitOne: "/api/v1/ingest/albums/submit-one",
    status: "/api/v1/ingest/status"
  },
  playlists: {
    list: "/api/v1/playlists/list",
    create: "/api/v1/playlists/create",
    sync: (id: string) => `/api/v1/playlists/${id}/sync`,
    reshuffle: (id: string) => `/api/v1/playlists/${id}/reshuffle`,
    reshuffleBulk: "/api/v1/playlists/reshuffle-bulk",
    delete: (id: string) => `/api/v1/playlists/${id}`
  },
  public: {
    playlists: "/api/v1/public/playlists"
  },
  metrics: {
    overview: "/api/v1/metrics/overview",
    history: "/api/v1/metrics/history"
  },
  library: {
    albums: "/api/v1/albums/list",
    tracks: "/api/v1/tracks/list",
    trackDetail: (id: string) => `/api/v1/tracks/detail/${id}`
  },
  settings: {
    root: "/api/v1/settings"
  },
  jobs: {
    list: "/api/v1/jobs/list",
    update: "/api/v1/jobs/update",
    history: "/api/v1/jobs/history"
  },
  assistant: {
    chat: "/api/v1/agent/chat"
  }
} as const;
