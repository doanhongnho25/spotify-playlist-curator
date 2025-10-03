# Product Requirements Document (PRD): Project Vibe MVP

| **Version** | **Date**   | **Author**      | **Status** |
|-------------|------------|-----------------|------------|
| 2.2         | 2025-10-01 | Ameya Phalke    | As-Built   |

## 1. Overview & Executive Summary

Project Vibe is a fun, mobile-first web application that generates personalized 10-song music playlists. It translates a user's typed 'vibe' into a curated list using an LLM and allows the user to save that playlist directly to their Spotify account with a single click.

## 2. Problem Statement

The current process for music discovery is overwhelming and often fails to capture specific, nuanced moods.

- **Problem 1: Choice Paralysis.** The sheer volume of music on streaming platforms makes finding the right song for a specific feeling a time-consuming chore.

- **Problem 2: Lack of Nuance.** Existing recommendation algorithms are poor at capturing abstract, culturally-relevant 'vibes'.

- **Problem 3: High-Friction Experience.** Even when a playlist is found, getting it into a user's library is a manual, multi-step process.

## 3. Target User Persona(s)

- **Persona Name:** Chloe the Creator

- **Role/Demographics:** Gen Z / Young Millennial (18-28). Highly active on social media.

- **Goals:**
  - To instantly find and save the perfect soundtrack for her mood or content.
  - To discover new, relevant music without tedious searching.

- **Frustrations:**
  - "It takes too many steps to get a list of songs I find online into my actual Spotify."
  - "I know the vibe I want, but I can't find a song that fits."

## 4. Goals & Core Hypothesis

### Business Goals

- Validate user demand for a "vibe-based" music discovery and creation tool.
- Achieve a high playlist creation and sharing rate, signaling strong product-market fit.

### Core Hypothesis

We believe that by building a simple app that translates vibes into playlists and saves them directly to Spotify with one click, our target user will discover and save music more effectively. We will know this is true when we see a high percentage of users authenticating with Spotify and successfully creating playlists.

## 5. MVP Scope & Features

| **Priority** | **Feature Name** | **User Story** | **Acceptance Criteria** |
|--------------|------------------|----------------|-------------------------|
| 1 (Must) | **Vibe-to-Playlist Generation** | As a user, I want to type my 'vibe' and get a 10-song playlist. | - UI has a text input and "Generate" button.<br>- Clicking "Generate" calls the backend and displays a verified list of 10 songs. |
| 2 (Must) | **Spotify Authentication** | As a user, I want to connect my Spotify account so the app can create playlists for me. | - A "Connect Spotify" button is present.<br>- Clicking it initiates the Spotify OAuth 2.0 login flow.<br>- After successful login, the UI updates to show a connected state with "Spotify Connected" badge.<br>- **As-Built:** Session managed via HTTP-only secure cookies (not localStorage).<br>- **As-Built:** Uses explicit IPv4 address (127.0.0.1) per Spotify redirect URI requirements. |
| 3 (Must) | **One-Click Playlist Creation** | As an authenticated user, I want to save the generated playlist to my Spotify account with one click. | - A "Save to Spotify" button appears with the generated playlist.<br>- Clicking it creates a new playlist in the user's Spotify account named after the vibe.<br>- The 10 songs are added to this new playlist.<br>- **As-Built:** Returns playlist URL with option to open in Spotify app.<br>- **As-Built:** Displays count of tracks successfully added. |
| 4 (Must) | **Share Vibe & Playlist** | As a user, I want to share my vibe and the resulting playlist on social media. | - A "Share" button is visible.<br>- Clicking it copies a pre-formatted text to the clipboard (e.g., "Feeling 'main character energy' and this is my vibe: [song list]").<br>- **As-Built:** Text-only sharing implemented (no visual/image generation). |

## 6. Success Metrics

- **Activation Rate:** % of unique visitors who generate at least one playlist. **Target:** > 40%

- **Authentication Rate:** % of users who generate a playlist and then successfully connect their Spotify account. **Target:** > 50%

- **Playlist Creation Rate:** % of authenticated users who successfully save a playlist to Spotify. **Target:** > 80%

## 7. Out of Scope

- Integrations with other music services (Apple Music, etc.).

- User accounts within our own system (authentication is handled solely by Spotify).

- Advanced RAG pipeline (we will stick with the un-grounded LLM for this MVP).

- **Visual/image-based social sharing** (text-only sharing implemented in MVP).

- **Automatic token refresh** (users must re-authenticate after token expiry).

- **Persistent session storage** (in-memory storage only in MVP; production requires database/Redis).

- **Multi-device session sync** (sessions are browser/device-specific).

## 8. Technical Implementation Notes (As-Built)

### Authentication
- OAuth 2.0 Authorization Code Flow fully implemented
- CSRF protection via state parameter
- HTTP-only cookies for secure token storage
- Session duration: 1 hour (Spotify access token expiry)
- Re-authentication required after session expiry

### Playlist Generation
- Uses Google Gemini AI (gemini-2.0-flash-exp model)
- Generates exactly 10 songs per vibe
- Song search and matching via Spotify Search API
- Tracks added count reported to user

### Known Limitations
- In-memory session storage (data lost on server restart)
- No token refresh automation
- Development mode only (25 user limit on Spotify app)
- Requires explicit IPv4 address (127.0.0.1) for local development

## 9. Production Readiness Gap

To move from MVP to production, the following must be addressed:

1. **Persistent Storage:** Implement Redis or database for session management
2. **Token Refresh:** Automate access token refresh using refresh tokens
3. **HTTPS Deployment:** Enable secure cookies in production environment
4. **Spotify App Status:** Move from Development to Extended Quota Mode
5. **Error Handling:** Enhanced user feedback for expired sessions and API failures
6. **Scalability:** Horizontal scaling support with shared session store

## Document Change Log

- **v2.1 (2025-09-30):** Initial approved version
- **v2.2 (2025-10-01):** Updated to reflect as-built implementation with technical notes and known limitations