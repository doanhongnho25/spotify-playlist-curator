# Architecture Design Brief: Project Vibe MVP v2.2

| **Version** | **Date**   | **Author**   | **Status** |
|-------------|------------|--------------|------------|
| 2.2         | 2025-10-01 | Ameya Phalke | As-Built   |

## 1. Overview & Goal

The goal is to design an architecture that supports the "one-click playlist creation" feature by implementing the Spotify OAuth 2.0 Authorization Code Flow. This will allow our application to securely obtain user permission to create and modify playlists on their behalf, providing a seamless user experience.

## 2. Proposed Tech Stack

| **Component** | **Technology / Framework / Service** | **Rationale** |
|---------------|--------------------------------------|---------------|
| **Frontend** | React | Best for handling the interactive UI and redirection logic required for OAuth. |
| **Backend** | Python (FastAPI) | Ideal for handling the server-side token exchange and making authenticated API calls to Spotify. |
| **Deployment** | Docker / Docker Compose | Provides a consistent, multi-service environment for local development. |
| **Environment Management** | .env file | Manages configuration variables for Spotify credentials, API keys, and service URLs. |
| **AI Model** | Not applicable | Gemini-powered vibe generation has been removed in favor of operator-driven curation. |
| **Other Tools** | Spotify Web API | User-authenticated endpoints for playlist creation and track search. |

## 3. High-Level Architecture: The OAuth 2.0 Flow

This architecture introduces a user authentication loop. The process is a standard, secure OAuth 2.0 flow.

1. **Initiate Login:** The user clicks "Connect Spotify" on our React frontend. The frontend redirects the user to Spotify's official authorization page.

2. **User Consent:** The user logs into Spotify and grants our app permission.

3. **Redirect with Code:** Spotify redirects the user back to our backend at the specified redirect_uri with a temporary authorization_code in the URL.

4. **Code Exchange:** Our FastAPI backend receives the authorization_code directly from Spotify's redirect.

5. **Token Request:** Our backend securely sends the authorization_code, along with our app's Client ID and Secret, to the Spotify token endpoint.

6. **Receive Tokens:** Spotify validates everything and returns an access_token and a refresh_token to our backend.

7. **Authenticated State:** The backend securely stores these tokens in memory (keyed by session_id) and sets an HTTP-only cookie. The backend then redirects the user back to the frontend. All subsequent playlist creation requests use this cookie to identify the user's session.

### Sequence Diagram

```
User → Frontend: Clicks "Connect Spotify"
Frontend → User: Redirect to Spotify login
User → Spotify: Logs in, grants permission
Spotify → Backend: Redirect to callback with Auth Code
Backend → Spotify: Exchanges Auth Code for Access Token
Spotify → Backend: Returns Access Token & Refresh Token
Backend → Backend: Stores tokens in memory (session_id)
Backend → Frontend: Sets HTTP-only cookie, redirects to frontend
Frontend → User: Displays "Connected" state
```

**As-Built Note:** Backend redirects directly to frontend after setting secure cookie (not via HTML with JavaScript).

## 4. API Endpoints (Contract)

Our API handles the authentication flow and authenticated actions.

| **Method** | **Endpoint** | **Description** |
|------------|--------------|-----------------|
| GET | /api/v1/auth/login | Redirects the user to the Spotify authorization URL with properly encoded parameters and CSRF state token. |
| GET | /api/v1/auth/callback | The endpoint Spotify redirects to. It validates CSRF state, exchanges the code for tokens, sets HTTP-only session cookie, and redirects to frontend. |
| GET | /api/v1/auth/status | Returns authentication status by checking for valid session cookie. No request body required. |
| POST | /api/v1/auth/logout | **[As-Built Addition]** Clears user session from server storage and deletes session cookie. |
| POST | /api/v1/playlist/create | **[Updated]** Accepts vibe and songs list in request body. Authentication handled via cookie (no session_id in body). Creates and populates a playlist for the logged-in user. Returns `status`, `playlist_id`, `playlist_url`, and `tracks_added`. |

### API Changes from Design

**Request Body Changes:**
- `/api/v1/playlist/create` no longer requires `session_id` in request body (handled via cookie)

**Response Additions:**
- `/api/v1/playlist/create` now returns:
  - `playlist_url`: Direct Spotify URL to open the playlist
  - `tracks_added`: Count of successfully matched and added tracks

## 5. Security & Scalability Considerations

### Security (CRITICAL) - As Implemented

- ✅ **Token Storage:** The user's access_token and refresh_token are stored server-side in memory, never exposed to the browser.

- ✅ **HTTP-Only Cookies:** Tokens are never stored in localStorage. The backend uses secure, HTTP-only cookies to maintain sessions, preventing XSS attacks.

- ✅ **CSRF Protection:** The state parameter is generated, stored server-side, and validated in the OAuth callback to prevent CSRF attacks.

- ✅ **Redirect URI Security:** Uses explicit IPv4 address (127.0.0.1) instead of localhost, per Spotify's security requirements.

- ⚠️ **HTTPS:** Currently using HTTP for local development. **Must enable HTTPS in production** with `secure=True` cookie flag.

- ⚠️ **Cookie Configuration:**
  - `httponly=True` - Prevents JavaScript access ✅
  - `secure=False` - Must be True in production ⚠️
  - `samesite='lax'` - CSRF protection ✅
  - `max_age=3600` - 1 hour expiry ✅

### Scalability - Current Limitations

- **In-Memory Storage:** The current implementation uses a Python dictionary (`user_tokens = {}`) for session storage. This approach:
  - ✅ Works perfectly for single-instance development/MVP
  - ❌ Does not persist across server restarts
  - ❌ Cannot be shared across multiple server instances
  - ❌ Limited by server memory

- **Production Requirements:**
  - Implement Redis or database-backed session storage
  - Enable horizontal scaling with shared session store
  - Add session cleanup/expiry background jobs
  - Implement connection pooling for database access

- **Token Refresh:** Current implementation does not automatically refresh expired tokens. Users must re-authenticate after 1 hour when access tokens expire.

## 6. Key Technical Risks

### Risk (Medium): Token Management Complexity
Securely handling the lifecycle of access tokens and refresh tokens adds complexity to the backend.

**Status:** Partially mitigated in MVP
- ✅ Secure storage implemented via in-memory dict
- ✅ HTTP-only cookies prevent client-side access
- ❌ No automatic token refresh (requires re-authentication)
- ❌ In-memory storage not production-ready

**Full Mitigation Plan:**
- Implement Redis for persistent session storage
- Add token refresh logic using refresh_token
- Set up background job to clean expired sessions

### Risk (Low): Token Expiration Handling
**[As-Built Addition]** Spotify access tokens expire after 1 hour. Current implementation requires user re-authentication rather than automatic refresh.

**Impact:** Users must reconnect Spotify if their session expires during use.

**Future Mitigation:** Implement automatic token refresh using the refresh_token provided by Spotify.

### Risk (Low): Rate Limiting
**[As-Built Addition]** Spotify API has rate limits that could affect users during high-traffic periods.

**Current Mitigation:** None implemented in MVP.

**Future Mitigation:** Implement request queuing and retry logic with exponential backoff.

## 7. Environment Configuration

**As-Built Implementation:** Uses `.env` file in project root for configuration management.

Required environment variables:

```bash
SPOTIFY_CLIENT_ID=<your_client_id>
SPOTIFY_CLIENT_SECRET=<your_client_secret>
FRONTEND_URL=http://127.0.0.1:3000
BACKEND_URL=http://127.0.0.1:8000
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Critical Notes:**
- Must use `127.0.0.1` not `localhost` (Spotify requirement)
- Spotify redirect URI in dashboard must exactly match `{BACKEND_URL}/api/v1/auth/callback`

## 8. Deployment Architecture

### Local Development (Current)
- Docker Compose orchestrates frontend and backend services
- Backend runs on port 8000, frontend on port 3000
- Services communicate via host network
- Environment variables loaded from `.env` file

### Production Requirements (Future)
1. **HTTPS/SSL:** Obtain SSL certificates, enable secure cookies
2. **Persistent Storage:** Deploy Redis or PostgreSQL for sessions
3. **Service URLs:** Update to production domain in environment variables
4. **Spotify App:** Move from Development to Extended Quota Mode
5. **Monitoring:** Add logging and error tracking (e.g., Sentry)
6. **Scaling:** Configure load balancer with session affinity or shared Redis store

## 9. Known Limitations & Technical Debt

### Current MVP Limitations
1. **Session Persistence:** In-memory storage means sessions lost on restart
2. **Token Refresh:** No automatic refresh; manual re-auth required
3. **User Limit:** Spotify Development Mode restricts to 25 test users
4. **Error Recovery:** Limited handling of token expiry during operations
5. **Multi-device:** No session synchronization across devices
6. **Production Security:** HTTP-only (must upgrade to HTTPS)

### Recommended Improvements for Production
1. Implement Redis-backed session store
2. Add automatic token refresh logic
3. Enhance error handling and user feedback
4. Add request logging and monitoring
5. Implement rate limiting and request queuing
6. Add health check endpoints for load balancer

## Document Change Log

- **v2.1 (2025-09-30):** Initial approved design
- **v2.2 (2025-10-01):** Updated to reflect as-built implementation with security details, limitations, and production readiness requirements