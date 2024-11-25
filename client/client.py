import socket
import os
import threading
from playsound import playsound

# Directory to save downloaded songs
DOWNLOAD_DIR = r"D:\SPIT\SPITTE\DC\music_app\client\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Server address (modify as needed)
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

# Global variable to control song playback
is_song_playing = False
song_thread = None

def send_request(sock, request):
    """Send a request to the server and receive a response."""
    try:
        print(f"Sending request to server: {request}")  # Debug log
        sock.send(request.encode())
        response = sock.recv(4096).decode()
        print(f"Received response: {response}")  # Debug log
        return response
    except Exception as e:
        print(f"Error while sending request: {e}")
        return "ERROR: Connection failed."

def list_playlists(sock):
    """Fetch and display available playlists."""
    response = send_request(sock, "LIST_PLAYLISTS|0")
    if "ERROR" in response:
        return []
    playlists = response.split("|")
    print("\nAvailable Playlists:")
    for i, playlist in enumerate(playlists, start=1):
        print(f"{i}. {playlist}")
    return playlists

def list_songs(sock, playlist):
    """Fetch and display available songs in a playlist."""
    response = send_request(sock, f"GET_SONGS|{playlist}|0")
    if "ERROR" in response:
        return []
    songs = response.split("|")
    print(f"\nSongs in '{playlist}' playlist:")
    for i, song in enumerate(songs, start=1):
        print(f"{i}. {song}")
    return songs

def get_lyrics(sock, playlist, song):
    """Fetch and display lyrics for a song."""
    response = send_request(sock, f"GET_LYRICS|{playlist}|{song}|0")
    print(f"\nLyrics for '{song}':\n{response}")

def download_song(sock, playlist, song):
    """Download a song from the server."""
    response = send_request(sock, f"PLAY_SONG|{playlist}|{song}|0")
    if response.startswith("ERROR"):
        print(response)
        return None
    song_path = os.path.join(DOWNLOAD_DIR, song)
    try:
        with open(song_path, "wb") as file:
            while True:
                data = sock.recv(4096)
                if data.endswith(b"EOF"):
                    file.write(data[:-3])  # Write the file without the EOF marker
                    break
                file.write(data)
        return song_path
    except Exception as e:
        print(f"Error while downloading the song: {e}")
        return None

def play_song_in_thread(song_path):
    """Play the song in a separate thread."""
    global is_song_playing
    try:
        is_song_playing = True
        print(f"Playing {os.path.basename(song_path)}...")
        playsound(song_path)
    except Exception as e:
        print(f"Error while playing the song: {e}")
    finally:
        is_song_playing = False

def play_song(sock, playlist, song):
    """Download and play a song."""
    global song_thread
    if is_song_playing:
        print("A song is already playing. Please pause it first.")
        return
    song_path = download_song(sock, playlist, song)
    if song_path:
        song_thread = threading.Thread(target=play_song_in_thread, args=(song_path,))
        song_thread.start()

def pause_song():
    """Pause the current song."""
    global is_song_playing, song_thread
    if is_song_playing:
        print("Pausing the current song...")
        # Stopping the thread playing the song (not graceful, as `playsound` has no pause support)
        is_song_playing = False
        if song_thread:
            song_thread.join(0.1)
            print("Song paused.")
    else:
        print("No song is currently playing.")

def main():
    """Main client program."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Connecting to server at {SERVER_IP}:{SERVER_PORT}...")
            client_socket.connect((SERVER_IP, SERVER_PORT))
            print("Connected to the server.")

            while True:
                print("\nMenu:")
                print("1. List Playlists")
                print("2. Select Playlist and View Songs")
                print("3. Select Song and Play")
                print("4. Get Lyrics")
                print("5. Pause Song")
                print("6. Exit")

                choice = input("Enter your choice: ")

                if choice == "1":
                    list_playlists(client_socket)
                elif choice == "2":
                    playlists = list_playlists(client_socket)
                    if playlists:
                        playlist_index = int(input("Select playlist: ")) - 1
                        if 0 <= playlist_index < len(playlists):
                            list_songs(client_socket, playlists[playlist_index])
                        else:
                            print("Invalid playlist selection.")
                elif choice == "3":
                    playlists = list_playlists(client_socket)
                    if playlists:
                        playlist_index = int(input("Select playlist: ")) - 1
                        if 0 <= playlist_index < len(playlists):
                            songs = list_songs(client_socket, playlists[playlist_index])
                            if songs:
                                song_index = int(input("Select song: ")) - 1
                                if 0 <= song_index < len(songs):
                                    play_song(client_socket, playlists[playlist_index], songs[song_index])
                                else:
                                    print("Invalid song selection.")
                elif choice == "4":
                    playlists = list_playlists(client_socket)
                    if playlists:
                        playlist_index = int(input("Select playlist: ")) - 1
                        if 0 <= playlist_index < len(playlists):
                            songs = list_songs(client_socket, playlists[playlist_index])
                            if songs:
                                song_index = int(input("Select song: ")) - 1
                                if 0 <= song_index < len(songs):
                                    get_lyrics(client_socket, playlists[playlist_index], songs[song_index])
                                else:
                                    print("Invalid song selection.")
                elif choice == "5":
                    pause_song()
                elif choice == "6":
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Try again.")
    except Exception as e:
        print(f"Error in client: {e}")

if __name__ == "__main__":
    main()
