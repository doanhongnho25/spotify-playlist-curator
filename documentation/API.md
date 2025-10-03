# Project Vibe API Reference

Base URL: `http://127.0.0.1:8000`

## Overview

The Project Vibe API provides endpoints for Spotify authentication and playlist management. All authenticated endpoints require a valid session cookie.

## Authentication

Authentication is handled via OAuth 2.0 with Spotify. Sessions are maintained using HTTP-only cookies.

### Session Cookie
- **Name:** `spotify_session`
- **Type:** HTTP-only, Lax SameSite
- **Duration:** 3600 seconds (1 hour)
- **Storage:** Server-side in-memory

---

## Endpoints

### Health Check

#### `GET /`

Check if the API is running and view configuration.

**Request:**
```http
GET / HTTP/1.1
Host: 127.0.0.1:8000
```

**Response:**
```json
{
  "status": "ok",
  "frontend_url": "http://127.0.0.1:3000",
  "backend_url": "http://127.0.0.1:8000"
}
```

**Status Codes:**
- `200 OK` - Service is running

---

## Authentication Endpoints

### Initiate Spotify Login

#### `GET /api/v1/auth/login`

Redirects the user to Spotify's authorization page to grant access.

**Request:**
```http
GET /api/v1/auth/login HTTP/1.1
Host: 127.0.0.1:8000
```

**Response:**
- `307 Temporary Redirect` to Spotify authorization URL

**Redirect URL Parameters:**
- `client_id` - Your Spotify client ID
- `response_type=code`
- `redirect_uri` - Callback URL
- `scope=playlist-modify-public playlist-modify-private`
- `state` - CSRF protection token

**Status Codes:**
- `307 Temporary Redirect` - Redirects to Spotify

**Notes:**
- Generates and stores a state parameter for CSRF protection
- User will be prompted to authorize the application on Spotify

---

### OAuth Callback

#### `GET /api/v1/auth/callback`

Handles the OAuth callback from Spotify after user authorization.

**Request:**
```http
GET /api/v1/auth/callback?code=AQA_Dyp6...&state=JYpo7kH... HTTP/1.1
Host: 127.0.0.1:8000
```

**Query Parameters:**
- `code` (required) - Authorization code from Spotify
- `state` (required) - CSRF state token

**Response:**
- `307 Temporary Redirect` to frontend URL
- Sets `spotify_session` cookie

**Status Codes:**
- `307 Temporary Redirect` - Success, redirects to frontend
- `400 Bad Request` - Invalid state or failed token exchange

**Error Response:**
```json
{
  "detail": "Invalid state parameter"
}
```

**Notes:**
- Exchanges authorization code for access and refresh tokens
- Stores tokens server-side
- Sets HTTP-only session cookie
- This endpoint is called by Spotify, not directly by the frontend

---

### Check Authentication Status

#### `GET /api/v1/auth/status`

Check if the current session is authenticated.

**Request:**
```http
GET /api/v1/auth/status HTTP/1.1
Host: 127.0.0.1:8000
Cookie: spotify_session=4k3K_Lrrci...
```

**Response:**
```json
{
  "authenticated": true
}
```

**Status Codes:**
- `200 OK` - Status check successful

**Notes:**
- Returns `false` if no valid session cookie
- Used by frontend to determine UI state

---

### Logout

#### `POST /api/v1/auth/logout`

Log out the current user and clear session.

**Request:**
```http
POST /api/v1/auth/logout HTTP/1.1
Host: 127.0.0.1:8000
Cookie: spotify_session=4k3K_Lrrci...
```

**Response:**
```json
{
  "status": "logged out"
}
```

**Status Codes:**
- `200 OK` - Logout successful

**Notes:**
- Deletes session from server storage
- Clears session cookie
- Safe to call even if not authenticated

---

## Playlist Endpoints

### Generate Playlist

#### `POST /api/v1/playlist/generate`

Generate a playlist of 10 songs based on a vibe using AI.

**Request:**
```http
POST /api/v1/playlist/generate HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "vibe": "cozy rainy day"
}
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| vibe | string | Yes | Description of the mood/vibe |

**Response:**
```json
{
  "songs": [
    {
      "title": "Dreams",
      "artist": "Fleetwood Mac"
    },
    {
      "title": "Sunday Morning",
      "artist": "Maroon 5"
    },
    ...
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| songs | array | Array of song objects |
| songs[].title | string | Song title |
| songs[].artist | string | Artist name |

**Status Codes:**
- `200 OK` - Playlist generated successfully
- `500 Internal Server Error` - AI generation failed

**Error Response:**
```json
{
  "detail": "Failed to generate playlist: <error message>"
}
```

**Notes:**
- Does not require authentication
- Uses Google Gemini AI
- Returns exactly 10 songs
- Songs may not exist on Spotify (verification happens during creation)

---

### Create Playlist on Spotify

#### `POST /api/v1/playlist/create`

Create a playlist in the authenticated user's Spotify account.

**Request:**
```http
POST /api/v1/playlist/create HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Cookie: spotify_session=4k3K_Lrrci...

{
  "vibe": "cozy rainy day",
  "songs": [
    {
      "title": "Dreams",
      "artist": "Fleetwood Mac"
    },
    ...
  ]
}
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| vibe | string | Yes | Original vibe description (used for playlist name) |
| songs | array | Yes | Array of song objects to add |
| songs[].title | string | Yes | Song title |
| songs[].artist | string | Yes | Artist name |

**Response:**
```json
{
  "status": "success",
  "playlist_id": "3cEYpjA9oz9GiPac4AsH4n",
  "playlist_url": "https://open.spotify.com/playlist/3cEYpjA9oz9GiPac4AsH4n",
  "tracks_added": 9
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" or error |
| playlist_id | string | Spotify playlist ID |
| playlist_url | string | Direct URL to open playlist in Spotify |
| tracks_added | integer | Number of tracks successfully added (may be less than requested) |

**Status Codes:**
- `200 OK` - Playlist created successfully
- `401 Unauthorized` - Not authenticated or session expired
- `400 Bad Request` - Failed to create playlist or get user info

**Error Responses:**

Not authenticated:
```json
{
  "detail": "Not authenticated"
}
```

Failed to create:
```json
{
  "detail": "Failed to create playlist: <error message>"
}
```

**Notes:**
- Requires valid authentication (session cookie)
- Creates a private playlist named "Vibe: {vibe}"
- Searches for each song on Spotify
- Only adds tracks that are found (tracks_added may be less than songs provided)
- Playlist is immediately available in user's Spotify account

---

## Error Responses

All endpoints may return the following error format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Request successful |
| 307 | Temporary Redirect | OAuth flow redirects |
| 400 | Bad Request | Invalid parameters, failed external API call |
| 401 | Unauthorized | Missing or invalid session cookie |
| 500 | Internal Server Error | Server error, AI generation failed |

---

## Authentication Flow

Complete OAuth 2.0 flow sequence:

1. Frontend calls `GET /api/v1/auth/login`
2. User redirected to Spotify
3. User authorizes app on Spotify
4. Spotify redirects to `GET /api/v1/auth/callback?code=...&state=...`
5. Backend exchanges code for tokens
6. Backend sets `spotify_session` cookie
7. Backend redirects to frontend
8. Frontend calls `GET /api/v1/auth/status` to verify
9. Frontend includes cookie in all subsequent requests

---

## Rate Limits

- **Spotify API:** Subject to Spotify's rate limits (varies by endpoint)
- **Gemini AI:** Subject to Google's rate limits
- **This API:** No rate limiting implemented in MVP

---

## CORS Configuration

**Allowed Origins:**
- `http://127.0.0.1:3000`
- `http://localhost:3000`

**Credentials:** Allowed (required for cookies)

**Methods:** All

**Headers:** All

---

## Development Notes

### Base URL
- Local: `http://127.0.0.1:8000`
- Must use IP address (not localhost) due to Spotify OAuth requirements

### Session Storage
- Current implementation uses in-memory storage
- Sessions lost on server restart
- Not suitable for production horizontal scaling

### Token Expiry
- Access tokens expire after 1 hour
- No automatic refresh implemented
- Users must re-authenticate after expiry

---

## Example Usage

### JavaScript/Frontend Example

```javascript
// Check auth status
const checkAuth = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/auth/status', {
    credentials: 'include' // Important: include cookies
  });
  const data = await response.json();
  return data.authenticated;
};

// Generate playlist
const generatePlaylist = async (vibe) => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/playlist/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vibe })
  });
  return await response.json();
};

// Create playlist
const createPlaylist = async (vibe, songs) => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/playlist/create', {
    method: 'POST',
    credentials: 'include', // Important: include cookies
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vibe, songs })
  });
  return await response.json();
};
```

### cURL Examples

Generate playlist:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/playlist/generate \
  -H "Content-Type: application/json" \
  -d '{"vibe": "summer vibes"}'
```

Check auth status:
```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/status \
  -b "spotify_session=your_session_id"
```

---

## Security Considerations

- Always use HTTPS in production
- Never expose session cookies to client-side JavaScript
- Validate all input on server side
- Session cookies are HTTP-only (XSS protection)
- State parameter prevents CSRF attacks
- Tokens stored server-side only