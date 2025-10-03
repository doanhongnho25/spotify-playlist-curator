import React, { useState, useEffect } from 'react';
import { Music, Sparkles, Check, Copy } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [vibe, setVibe] = useState('');
  const [playlist, setPlaylist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Check authentication status on mount
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/status`, {
        credentials: 'include', // CRITICAL: Include cookies in request
      });
      const data = await res.json();
      setIsAuthenticated(data.authenticated);
    } catch (err) {
      console.error('Error checking auth status:', err);
      setIsAuthenticated(false);
    }
  };

  const handleGenerate = async () => {
    if (!vibe.trim()) return;
    
    setLoading(true);
    setPlaylist(null);
    setSaved(false);

    try {
      const res = await fetch(`${API_BASE}/api/v1/playlist/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vibe: vibe.trim() })
      });
      
      if (!res.ok) {
        throw new Error('Failed to generate playlist');
      }
      
      const data = await res.json();
      setPlaylist(data);
    } catch (err) {
      console.error('Error generating playlist:', err);
      alert('Failed to generate playlist. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE}/api/v1/auth/login`;
  };

  const handleSave = async () => {
    if (!playlist) return;
    
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/playlist/create`, {
        method: 'POST',
        credentials: 'include', // CRITICAL: Include cookies in request
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          vibe: vibe.trim(),
          songs: playlist.songs,
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setSaved(true);
        console.log('Playlist created:', data);
        
        // Optional: Open the playlist in Spotify
        if (data.playlist_url) {
          setTimeout(() => {
            if (window.confirm('Playlist saved! Open in Spotify?')) {
              window.open(data.playlist_url, '_blank');
            }
          }, 500);
        }
        
        setTimeout(() => setSaved(false), 3000);
      } else {
        const error = await res.json();
        if (res.status === 401) {
          alert('Session expired. Please reconnect your Spotify account.');
          setIsAuthenticated(false);
        } else {
          alert(`Failed to save playlist: ${error.detail || 'Unknown error'}`);
        }
      }
    } catch (err) {
      console.error('Error saving playlist:', err);
      alert('Failed to save playlist. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleShare = () => {
    if (!playlist) return;
    
    const songList = playlist.songs
      .map((s, i) => `${i + 1}. ${s.title} - ${s.artist}`)
      .join('\n');
    const text = `Feeling '${vibe}' and this is my vibe:\n\n${songList}\n\nCreated with Project Vibe 🎵`;
    
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Music className="w-10 h-10" />
            <h1 className="text-5xl font-bold">Project Vibe</h1>
          </div>
          <p className="text-xl text-purple-200">Turn your vibe into a playlist</p>
        </div>

        <div className="mb-8 text-center">
          {!isAuthenticated ? (
            <button
              onClick={handleConnect}
              className="bg-green-500 hover:bg-green-600 text-white font-semibold px-6 py-3 rounded-full transition-all transform hover:scale-105"
            >
              Connect Spotify
            </button>
          ) : (
            <div className="inline-flex items-center gap-2 bg-green-500/20 border border-green-500 text-green-300 px-4 py-2 rounded-full">
              <Check className="w-5 h-5" />
              <span>Spotify Connected</span>
            </div>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl mb-8">
          <label className="block text-lg font-semibold mb-3">What's your vibe?</label>
          <input
            type="text"
            value={vibe}
            onChange={(e) => setVibe(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
            placeholder="e.g., main character energy, cozy rainy day, late night drive..."
            className="w-full bg-white/20 border border-white/30 rounded-xl px-4 py-3 text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
          
          <button
            onClick={handleGenerate}
            disabled={loading || !vibe.trim()}
            className="mt-4 w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl transition-all transform hover:scale-105 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Playlist
              </>
            )}
          </button>
        </div>

        {playlist && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Music className="w-6 h-6" />
              Your Playlist
            </h2>
            
            <div className="space-y-3 mb-6">
              {playlist.songs.map((song, idx) => (
                <div key={idx} className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="text-purple-300 font-semibold w-6">{idx + 1}.</span>
                    <div className="flex-1">
                      <div className="font-semibold">{song.title}</div>
                      <div className="text-sm text-purple-200">{song.artist}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleSave}
                disabled={!isAuthenticated || saving || saved}
                className="flex-1 bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
              >
                {saved ? (
                  <>
                    <Check className="w-5 h-5" />
                    Saved to Spotify!
                  </>
                ) : saving ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Music className="w-5 h-5" />
                    Save to Spotify
                  </>
                )}
              </button>

              <button
                onClick={handleShare}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-xl transition-all flex items-center gap-2"
              >
                {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                {copied ? 'Copied!' : 'Share'}
              </button>
            </div>

            {!isAuthenticated && (
              <p className="text-sm text-purple-200 mt-4 text-center">
                Connect your Spotify account to save playlists
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}