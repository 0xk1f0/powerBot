import spotipy
import datetime
import toml
import json
import os

# Load the config.toml file
config = toml.load("config.toml")

# Extract the client ID and client secret from the config file
ID = config["spotify"]["client_id"]
SECRET = config["spotify"]["client_secret"]

def save_as_json(fetched_playlist, submitter_name):
    # Extract the playlist name and owner from the JSON object
    playlist_name = fetched_playlist["name"]
    playlist_owner = fetched_playlist["owner"]["display_name"]
    # Extract the list of tracks from the playlist information
    tracks = fetched_playlist["tracks"]["items"]

    songs = []

    for track in tracks:
        entry = {
            'name': f'{track["track"]["name"]}',
            'artist': f'{track["track"]["artists"][0]["name"]}',
            'url': f'{track["track"]["external_urls"]["spotify"]}'
        }
        songs.append(entry)

    json_obj = {
        "name": f"{playlist_name}",
        "owner": f"{playlist_owner}",
        "for": f"{submitter_name}",
        "songs": songs
    }

    # Open the json file for writing
    with open(os.path.join(f"{os.getcwd()}/data", "playlist.json"), "w") as f:
        # Write to file
        json.dump(json_obj, f, indent=4)

def save_as_txt(fetched_playlist, submitter_name):
    # Extract the playlist name and owner from the JSON object
    playlist_name = fetched_playlist["name"]
    playlist_owner = fetched_playlist["owner"]["display_name"]
    # Extract the list of tracks from the playlist information
    tracks = fetched_playlist["tracks"]["items"]
    # Extract the URLs from the items
    urls = [track["track"]["external_urls"]["spotify"] for track in tracks]

    # Find the length of the longest URL, artist name, and song name in the list
    max_url_length = max(len(url) for url in urls)
    max_artist_length = max(len(track["track"]["artists"][0]["name"]) for track in tracks)
    max_song_length = max(len(track["track"]["name"]) for track in tracks)

    # Calculate the width of the table based on the length of the longest values
    table_width = max(max_url_length, max_artist_length, max_song_length) + 4

    # Create the table header using ASCII symbols
    header = "+" + "-"*(table_width*3 + 2) + "+"

    # Print the column headers
    desc = "| {:^{width}} | {:^{width}} | {:^{width}} |".format(
        "Artist", "Song", "URL", width=table_width-2
    )

    # Open the text file for writing
    with open(os.path.join(f"{os.getcwd()}/data", "playlist.txt"), "w") as f:
        # Write the playlist name and owner at the top of the file
        f.write("Name: " + playlist_name + "\n")
        f.write("Owner: " + playlist_owner + "\n")
        f.write("For: " + submitter_name + "\n")

        # Write the current date and time at the top of the file
        f.write("Generated on: " + str(datetime.datetime.now()) + "\n")

        # Write the table header to the file
        f.write(header + "\n")

        # Write the column headers to the file
        f.write(desc + "\n")

        # Write a separator line to the file
        f.write(header + "\n")

        # Iterate through the list of tracks and write the URL, artist name, and song name
        # in a row of the table
        for track in tracks:
            url = track["track"]["external_urls"]["spotify"]
            artist = track["track"]["artists"][0]["name"]
            song = track["track"]["name"]
            row = "| {:<{width}} | {:<{width}} | {:<{width}} |".format(
                song, artist, url, width=table_width-2
            )
            f.write(row + "\n")

        # Write last separator line to the file
        f.write(header + "\n")

def perform_archive(url, format, add_name):
    # Obtain an access token and refresh token using the prompt_for_user_token function
    token = spotipy.util.prompt_for_user_token(
        "cosmic",
        scope="playlist-read-private playlist-read-collaborative",
        client_id=ID,
        client_secret=SECRET,
        redirect_uri="http://localhost:8888/callback"
    )

    # Extract the playlist ID from the URL
    playlist_id = url.split("/")[-1]

    try:
        # Create a Spotify object using the access token
        spotify = spotipy.Spotify(auth=token)
        # Retrieve the playlist information using the playlist() method
        playlist = spotify.playlist(playlist_id)
    except:
        return False

    if format == "json":
        save_as_json(playlist, add_name)
    elif format == "txt":
        save_as_txt(playlist, add_name)
    else:
        return False
