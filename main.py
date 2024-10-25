import os
import requests
import datetime
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Loading of environment variables
load_dotenv()

# Defines
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_USERNAME = os.getenv("SPOTIFY_USERNAME")
SPOTIFY_REDIRECT_URI = "https://open.spotify.com/"
SPOTIFY_SCOPE = 'playlist-modify-private'
URL = "https://www.billboard.com/charts/hot-100"
HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
}

# Evaluates the date to ensure if it is a ISO format or not
date_of_travel = ""
evaluation_of_date = True
while evaluation_of_date:
    date_of_travel = input("Enter the date you would like to travel to. Type the date in this format YYYY-MM-DD: ")
    try:
        datetime.date.fromisoformat(date_of_travel)
        evaluation_of_date = False
    except ValueError:
        raise ValueError("Please enter a valid date in this format: YYYY-MM-DD")

if date_of_travel == "":
    date_of_travel = datetime.date.today()

# Makes request to "billboard.com" to get top 100 songs chart of specific data.
response = requests.get(url = f"{URL}/{date_of_travel}", headers = HEADER)
response.raise_for_status()

# Creates a beautiful soup object in order to scrape to find songs-artists of chart.
soup = BeautifulSoup(response.text, "html.parser")
chart_rows = soup.find_all(name = "div", class_ = "o-chart-results-list-row-container")
titles = []
artists = []
for row in chart_rows:
    title = row.find(id="title-of-a-story").get_text().replace("\n", "").replace("\t", "")
    artist = row.find(name="span", class_="a-no-trucate").get_text().replace("\n", "").replace("\t", "")
    titles.append(title)
    artists.append(artist)

# Creates spotify object and authenticates the API's client by returning token.
sp = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(
        client_id = SPOTIFY_CLIENT_ID,
        client_secret = SPOTIFY_CLIENT_SECRET,
        redirect_uri = SPOTIFY_REDIRECT_URI,
        scope = SPOTIFY_SCOPE,
        cache_path="token.txt",
    )
)

# Gets spotify user's account id.
user_id = sp.current_user()["id"]

# Search all songs by URLs of spotify.
song_uris = []
year = date_of_travel.split("-")[0]
for song in titles:
    result = sp.search(q=f"track:{song} artist:{artists[titles.index(song)]} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creates playlist object with all songs where find.
playlist = sp.user_playlist_create(user = user_id, name = f"{date_of_travel} Billboard", public = False)

# Adds playlist in spotify account.
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)