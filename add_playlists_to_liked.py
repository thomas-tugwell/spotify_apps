import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify App Credentials
CLIENT_ID = 'your_client_ID'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# Scope to read playlists and add to liked songs
SCOPE = 'playlist-read-private playlist-read-collaborative user-library-read user-library-modify'

# Create Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

def get_all_playlists():
    playlists = []
    limit = 50
    offset = 0
    while True:
        response = sp.current_user_playlists(limit=limit, offset=offset)
        playlists.extend(response['items'])
        if response['next']:
            offset += limit
        else:
            break
    return playlists

def get_tracks_from_playlist(playlist_id):
    tracks = []
    offset = 0
    while True:
        results = sp.playlist_items(playlist_id, offset=offset)
        items = results['items']
        if not items:
            break
        for item in items:
            track = item.get('track')
            if track and track.get('id'):
                tracks.append(track['id'])
        offset += len(items)
    return tracks

def get_all_liked_track_ids():
    liked_ids = set()
    limit = 50
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results['items']
        if not items:
            break
        liked_ids.update(item['track']['id'] for item in items if item.get('track'))
        offset += limit
    return liked_ids

def add_tracks_to_liked(tracks_to_add):
    BATCH_SIZE = 50
    for i in range(0, len(tracks_to_add), BATCH_SIZE):
        batch = tracks_to_add[i:i+BATCH_SIZE]
        sp.current_user_saved_tracks_add(batch)
        print(f"Added {len(batch)} tracks to Liked Songs.")

# --- Main Execution ---
print("Fetching all your playlists...")
all_playlists = get_all_playlists()

print("Collecting all track IDs from playlists...")
playlist_track_ids = set()
for pl in all_playlists:
    name = pl['name']
    pl_id = pl['id']
    print(f"→ Fetching from playlist: {name}")
    track_ids = get_tracks_from_playlist(pl_id)
    playlist_track_ids.update(track_ids)

print(f"\nTotal unique tracks found in playlists: {len(playlist_track_ids)}")

print("Fetching existing liked songs...")
liked_track_ids = get_all_liked_track_ids()
print(f"Currently liked songs: {len(liked_track_ids)}")

# Determine which tracks are new
tracks_to_add = list(playlist_track_ids - liked_track_ids)
print(f"New tracks to add to liked songs: {len(tracks_to_add)}")

# Add them
if tracks_to_add:
    add_tracks_to_liked(tracks_to_add)
else:
    print("All tracks already liked — nothing to add.")
