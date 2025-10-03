from fastapi import FastAPI, HTTPException, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import httpx
import secrets
import os
from typing import Optional
from urllib.parse import urlencode
import google.generativeai as genai

app = FastAPI()

# Determine if running in Docker or locally
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# CORS configuration - allow frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify OAuth Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = f"{BACKEND_URL}/api/v1/auth/callback"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# In-memory token storage (keyed by session_id)
user_tokens = {}
# In-memory state storage (for CSRF protection)
state_store = {}

class VibeRequest(BaseModel):
    vibe: str

class PlaylistCreateRequest(BaseModel):
    vibe: str
    songs: list

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "frontend_url": FRONTEND_URL,
        "backend_url": BACKEND_URL
    }

@app.get("/api/v1/auth/login")
async def login():
    """Initiates the Spotify OAuth flow"""
    state = secrets.token_urlsafe(16)
    state_store[state] = True  # Store state for CSRF validation
    
    scope = "playlist-modify-public playlist-modify-private"
    
    # Properly URL encode the parameters
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
        "state": state,
        "show_dialog": "false"  # Set to "true" for testing to always show auth dialog
    }
    
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    print(f"Redirecting to Spotify auth: {auth_url}")
    return RedirectResponse(auth_url)

@app.get("/api/v1/auth/callback")
async def callback(code: str, state: str, response: Response):
    """Handles the OAuth callback from Spotify"""
    
    print(f"Callback received - code: {code[:10]}..., state: {state}")
    
    # CSRF protection - validate state
    if state not in state_store:
        print(f"Invalid state: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del state_store[state]
    
    async with httpx.AsyncClient() as client:
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        }
        
        print(f"Exchanging code for token with redirect_uri: {SPOTIFY_REDIRECT_URI}")
        
        token_response = await client.post(
            SPOTIFY_TOKEN_URL,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_response.status_code != 200:
            print(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to get access token: {token_response.text}"
            )
        
        tokens = token_response.json()
        print("Successfully received tokens from Spotify")
        
        # Generate secure session ID
        session_id = secrets.token_urlsafe(32)
        
        # Store tokens server-side
        user_tokens[session_id] = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
        }
        
        print(f"Created session: {session_id[:10]}...")
        
        # Set HTTP-only, secure cookie (as per ADB requirements)
        response = RedirectResponse(url=FRONTEND_URL)
        response.set_cookie(
            key="spotify_session",
            value=session_id,
            httponly=True,  # Prevents XSS attacks
            secure=False,    # Set to True in production with HTTPS
            samesite="lax",  # CSRF protection
            max_age=3600,    # 1 hour
            domain=None,     # Will use current domain
            path="/"
        )
        
        return response

@app.get("/api/v1/auth/status")
async def auth_status(spotify_session: Optional[str] = Cookie(None)):
    """Check if user is authenticated"""
    authenticated = spotify_session is not None and spotify_session in user_tokens
    print(f"Auth status check - session: {spotify_session[:10] if spotify_session else None}..., authenticated: {authenticated}")
    return {"authenticated": authenticated}

@app.post("/api/v1/auth/logout")
async def logout(response: Response, spotify_session: Optional[str] = Cookie(None)):
    """Log out the user"""
    if spotify_session and spotify_session in user_tokens:
        del user_tokens[spotify_session]
        print(f"Logged out session: {spotify_session[:10]}...")
    
    response.delete_cookie(key="spotify_session", path="/")
    return {"status": "logged out"}

@app.post("/api/v1/playlist/generate")
async def generate_playlist(request: VibeRequest):
    """Generate a playlist using Gemini AI"""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    prompt = f"""Generate a playlist of exactly 10 songs that match this vibe: "{request.vibe}"

Return ONLY a JSON array with this exact format, no other text:
[
  {{"title": "Song Name", "artist": "Artist Name"}},
  ...
]

Make sure the songs are real, popular songs that match the vibe. Be creative and diverse in your selections."""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        import json
        # Clean up markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        songs = json.loads(response_text.strip())
        print(f"Generated {len(songs)} songs for vibe: {request.vibe}")
        
        return {"songs": songs}
    except Exception as e:
        print(f"Error generating playlist: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate playlist: {str(e)}")

@app.post("/api/v1/playlist/create")
async def create_playlist(
    request: PlaylistCreateRequest,
    spotify_session: Optional[str] = Cookie(None)
):
    """Create a playlist on Spotify for the authenticated user"""
    
    print(f"Create playlist request - session: {spotify_session[:10] if spotify_session else None}...")
    
    # Check authentication via cookie
    if not spotify_session or spotify_session not in user_tokens:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    access_token = user_tokens[spotify_session]["access_token"]
    
    async with httpx.AsyncClient() as client:
        # Get user profile
        user_response = await client.get(
            f"{SPOTIFY_API_BASE}/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"Failed to get user info: {user_response.status_code} - {user_response.text}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to get user info: {user_response.text}"
            )
        
        user_id = user_response.json()["id"]
        print(f"Creating playlist for user: {user_id}")
        
        # Create playlist
        playlist_response = await client.post(
            f"{SPOTIFY_API_BASE}/users/{user_id}/playlists",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": f"Vibe: {request.vibe}",
                "description": f"Generated by Project Vibe for the mood: {request.vibe}",
                "public": False,
            }
        )
        
        if playlist_response.status_code not in [200, 201]:
            print(f"Failed to create playlist: {playlist_response.status_code} - {playlist_response.text}")
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to create playlist: {playlist_response.text}"
            )
        
        playlist_id = playlist_response.json()["id"]
        playlist_url = playlist_response.json()["external_urls"]["spotify"]
        print(f"Created playlist: {playlist_id}")
        
        # Search for and add tracks
        track_uris = []
        for song in request.songs:
            search_query = f"{song['title']} {song['artist']}"
            search_response = await client.get(
                f"{SPOTIFY_API_BASE}/search",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "q": search_query,
                    "type": "track",
                    "limit": 1,
                }
            )
            
            if search_response.status_code == 200:
                results = search_response.json()
                if results["tracks"]["items"]:
                    track_uris.append(results["tracks"]["items"][0]["uri"])
        
        print(f"Found {len(track_uris)} tracks out of {len(request.songs)} songs")
        
        # Add tracks to playlist
        if track_uris:
            add_tracks_response = await client.post(
                f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"uris": track_uris}
            )
            
            if add_tracks_response.status_code not in [200, 201]:
                print(f"Warning: Failed to add some tracks: {add_tracks_response.text}")
        
        return {
            "status": "success", 
            "playlist_id": playlist_id,
            "playlist_url": playlist_url,
            "tracks_added": len(track_uris)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)