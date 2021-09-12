import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import json
import os
from pprint import pprint

# needs to have Spotify App created in the developer dashboard
CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
REDIRECT_URI = "http://127.0.0.1:5500/"
SCOPE = "playlist-modify-private"

date = input("What year do you want to travel to? \n"
             "Type the date in this format YYYY-MM-DD: ")

year = date.split("-")[0]

url = f"https://www.billboard.com/charts/hot-100/{date}"

# scrapes top 100 songs data from Billboard website
data = requests.get(url)
songs_webpage = data.text
soup = BeautifulSoup(songs_webpage, "html.parser")

# retrieves songs titles using list comprehension
all_songs = soup.select(".chart-element__information__song")
songs_titles = [song.getText() for song in all_songs]
print(songs_titles)

# creates SpotifyOAuth object and passes it as a parameter to
# with OAuth it allows this application to access an account without giving a username and password
my_spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,   # redirect URI of this application
    scope=SCOPE,
    cache_path="token.txt"))  # path to location to save tokens

# gets the user id of the authenticated user
user_id = my_spotify.current_user()["id"]

songs_uri = []
search_url = "https://api.spotify.com/v1/search"

# create a list of Spotify song URIs for the list of song names
with open("token.txt") as file:
    # read file as json and get the token
    contents = json.loads(file.read())
    token = contents["access_token"]
    for song in songs_titles:
        # uses this query format to narrow down on a track name for a particular year
        songs_result = my_spotify.search(q=f"track:{song} year:{year}", type="track")
        try:
            song_uri = songs_result["tracks"]["items"][0]["uri"]
            songs_uri.append(song_uri)
        except IndexError:
            # if the song in not available in Spotify
            print(f"Song '{song}' not found in Spotify")

# creates a new spotify playlist
playlist = my_spotify.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
playlist_id = playlist["id"]
# adds all the songs uri's to the playlist
my_spotify.playlist_add_items(playlist_id=playlist_id, items=songs_uri)
