# Project Vibe - Architecture Documentation

## System Overview

Project Vibe is a containerized web application that uses AI to generate personalized Spotify playlists based on user-described "vibes". The system consists of two main services that communicate via REST API.

## High-Level Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Browser   │ ◄─────► │   Frontend  │ ◄─────► │   Backend    │
│             │         │   (React)   │         │  (FastAPI)   │
└─────────────┘         └─────────────┘         └──────────────┘
                              │                        │
                              │                        ├─────► Spotify API
                              │                        │
                              │                        └─────► Google Gemini AI
```

## Component Architecture

### Frontend (React)
**Technology:** React 18.2.0  
**Port:** 3000  
**Container:** Node 18 Alpine

**Responsibilities:**
- User interface rendering
- User input collection (vibe text)
- OAuth redirect handling
- API communication with backend
- Session state management via cookies

**Key Components:**
- `App.js` - Main application component
- HTTP client with `credentials: 'include'` for cookie support

**External Dependencies:**
- `lucide-react` - Icon library
- Tailwind CSS (via CDN) - Styling

### Backend (FastAPI)
**Technology:** Python 3.11 with FastAPI  
**Port:** 8000  
**Container:** Python 3.11 Slim

**Responsibilities:**
- OAuth 2.0 flow orchestration
- Session management and token storage
- Spotify API integration
- Gemini AI integration for playlist generation
- CORS handling

**Key Modules:**
- OAuth handlers (`/api/v1/auth/*`)
- Playlist generation (`/api/v1/playlist/generate`)
- Playlist creation (`/api/v1/playlist/create`)

**External Dependencies:**
- `fastapi` - Web framework
- `httpx` - Async HTTP client
- `google-generativeai` - AI integration
- `pydantic` - Data validation

## Data Flow

### Authentication Flow
```
1. User clicks "Connect Spotify"
   └─> Frontend redirects to Backend /api/v1/auth/login

2. Backend generates state token and redirects to Spotify
   └─> User authorizes on Spotify

3. Spotify redirects to Backend /api/v1/auth/callback with code
   └─> Backend exchanges code for access_token

4. Backend stores tokens in memory (session_id → tokens)
   └─> Sets HTTP-only cookie with session_id

5. Backend redirects to Frontend
   └─> Frontend checks /api/v1/auth/status
   └─> Displays "Spotify Connected"
```

### Playlist Generation Flow
```
1. User enters vibe text and clicks "Generate"
   └─> Frontend POST /api/v1/playlist/generate

2. Backend calls Gemini AI with prompt
   └─> Gemini returns JSON array of 10 songs

3. Backend returns song list to Frontend
   └─> Frontend displays playlist

4. User clicks "Save to Spotify"
   └─> Frontend POST /api/v1/playlist/create (with cookie)

5. Backend validates session from cookie
   └─> Gets user's Spotify profile
   └─> Creates empty playlist
   └─> Searches for each song
   └─> Adds tracks to playlist

6. Backend returns playlist URL
   └─> Frontend displays success + optional open in Spotify
```

## Security Architecture

### Authentication & Authorization
- **OAuth 2.0 Authorization Code Flow** for Spotify integration
- **State parameter** for CSRF protection
- **HTTP-only cookies** for session management
- Server-side token storage (not exposed to client)

### Data Protection
- Tokens stored in memory (not database in MVP)
- No sensitive data in localStorage
- CORS configured for specific origin only
- Cookie attributes:
  - `httponly=True` - Prevents XSS
  - `samesite='lax'` - CSRF protection
  - `max_age=3600` - 1 hour expiry

### API Security
- All authenticated endpoints validate session cookie
- Invalid sessions return 401 Unauthorized
- Redirect URIs use explicit IP (127.0.0.1) per Spotify requirements

## Storage Architecture

### Current (MVP)
```python
# In-memory dictionary
user_tokens = {
    'session_id_abc123': {
        'access_token': 'BQA...',
        'refresh_token': 'AQD...',
        'expires_in': 3600
    }
}

state_store = {
    'state_xyz789': True
}
```

**Limitations:**
- Data lost on server restart
- Cannot scale horizontally
- No persistence across deployments

### Future (Production)
```
Redis or PostgreSQL
├── sessions (session_id → user_data)
├── tokens (session_id → spotify_tokens)
└── state (state_token → expiry_time)
```

## Deployment Architecture

### Local Development
```
Docker Compose
├── Frontend Container (port 3000)
│   └── React Dev Server
├── Backend Container (port 8000)
│   └── Uvicorn (FastAPI)
└── Network: bridge (default)
```

### Environment Configuration
- `.env` file in root directory
- Variables injected into containers via docker-compose
- Frontend reads `REACT_APP_*` variables at build time
- Backend reads variables at runtime

### Production Considerations
1. **HTTPS/SSL** - Required for secure cookies
2. **Load Balancer** - Session affinity or shared Redis
3. **Database** - PostgreSQL for session persistence
4. **Monitoring** - Application logs, error tracking
5. **Scaling** - Horizontal scaling with shared session store

## API Integration Architecture

### Spotify Web API
**Base URL:** `https://api.spotify.com/v1`

**Endpoints Used:**
- `GET /me` - Get user profile
- `POST /users/{user_id}/playlists` - Create playlist
- `GET /search` - Search for tracks
- `POST /playlists/{playlist_id}/tracks` - Add tracks

**Authentication:** Bearer token in Authorization header

### Google Gemini AI
**Model:** `gemini-2.0-flash-exp`

**Usage:**
- Prompt engineering for playlist generation
- Returns JSON array of songs
- Handles markdown code block cleanup

## Performance Considerations

### Frontend
- React dev server for hot reload
- Tailwind CSS loaded via CDN (no build step)
- Minimal JavaScript bundle

### Backend
- Async HTTP client (httpx) for concurrent API calls
- FastAPI async endpoints for non-blocking I/O
- In-memory storage for fast lookups

### Bottlenecks
- Serial Spotify search requests (10 songs)
- Gemini AI response time (2-5 seconds)
- No caching layer

## Error Handling

### Frontend
- User-friendly error messages
- Session expiry detection (401 → prompt re-auth)
- Console logging for debugging

### Backend
- HTTP exception handling with status codes
- Detailed logging to stdout
- Graceful degradation (e.g., tracks not found)

## Monitoring & Observability

### Current
- Docker logs (`docker-compose logs`)
- Backend prints debug information
- Frontend console.log statements

### Production Recommendations
- Structured logging (JSON format)
- Error tracking (Sentry, Rollbar)
- Performance monitoring (APM)
- Health check endpoints

## Scalability Path

### Phase 1: MVP (Current)
- Single instance
- In-memory storage
- 25 user limit (Spotify dev mode)

### Phase 2: Production
- Redis for sessions
- Multiple backend instances
- Load balancer with session affinity

### Phase 3: Scale
- Horizontal auto-scaling
- CDN for frontend
- Database connection pooling
- Caching layer (Redis)

## Technology Decisions

### Why FastAPI?
- Native async support
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Fast performance

### Why React?
- Component-based architecture
- Large ecosystem
- OAuth redirect handling
- Simple state management

### Why Docker?
- Consistent environments
- Easy local development
- Production parity
- Service isolation

### Why In-Memory Storage?
- Simplicity for MVP
- Zero infrastructure dependencies
- Fast development iteration
- Known limitation to address later

## System Constraints

### Hard Limits
- Spotify API rate limits (varies by endpoint)
- Gemini API rate limits
- 1-hour token expiry
- 25 user limit in development mode

### Soft Limits
- Memory constraints (token storage)
- Single region deployment
- No request queuing
- No retry logic

## Future Architecture Enhancements

1. **Caching Layer** - Cache Spotify search results
2. **Queue System** - Background playlist creation
3. **WebSockets** - Real-time playlist creation updates
4. **CDN** - Static asset delivery
5. **Multi-Region** - Geographic distribution
6. **Microservices** - Separate playlist service
7. **Analytics** - User behavior tracking
8. **A/B Testing** - Feature experimentation platform