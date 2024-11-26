import socket
import os
import pygame
import threading
import time

# Directory to save downloaded songs
DOWNLOAD_DIR = r"D:\SPIT\SPITTE\DC\music_app\client\downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Server address
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

# Flag for pausing the song
pause_playing = False
song_thread = None

def send_request(sock, request):
    """Send a request to the server and receive a response."""
    sock.send(request.encode())
    # If the request is for a song, the response will be binary data, not text
    if request.startswith("PLAY_SONG"):
        response = b""
        while True:
            data = sock.recv(4096)
            if data.endswith(b"EOF"):
                response += data[:-3]  # Remove EOF marker
                break
            response += data
        return response  # Return binary data (song file)
    else:
        # If not a song request, handle as text response
        response = sock.recv(4096).decode()
        return response

def list_playlists(sock):
    """Fetch and display available playlists."""
    response = send_request(sock, "LIST_PLAYLISTS|0")
    playlists = response.split("|")
    print("Available Playlists:")
    for i, playlist in enumerate(playlists, start=1):
        print(f"{i}. {playlist}")
    return playlists

def list_songs(sock, playlist):
    """Fetch and display available songs in a playlist."""
    response = send_request(sock, f"GET_SONGS|{playlist}|0")
    songs = response.split("|")
    print(f"Songs in '{playlist}' playlist:")
    for i, song in enumerate(songs, start=1):
        print(f"{i}. {song}")
    return songs

def get_lyrics(sock, playlist, song):
    """Fetch and display lyrics for a song."""
    response = send_request(sock, f"GET_LYRICS|{playlist}|{song}|0")
    print(f"Lyrics for '{song}':\n{response}")

def play_song(sock, playlist, song):
    """Fetch a song from the server and play it."""
    global song_thread, pause_playing
    response = send_request(sock, f"PLAY_SONG|{playlist}|{song}|0")
    if response.startswith(b"ERROR"):
        print(response.decode())
    else:
        # Save the received song as a file
        song_path = os.path.join(DOWNLOAD_DIR, song)
        with open(song_path, "wb") as file:
            file.write(response)

        print(f"Playing {song}...")

        # Start the song playback in a separate thread
        song_thread = threading.Thread(target=play_song_thread, args=(song_path,))
        song_thread.start()

def play_song_thread(song_path):
    """Play the song in a separate thread using pygame."""
    global pause_playing
    try:
        # Handle spaces in file paths by wrapping the path in double quotes
        if not os.path.isfile(song_path):
            print(f"Song file {song_path} does not exist.")
            return

        print(f"Playing song: {song_path}")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load the song and play it
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if pause_playing:
                pygame.mixer.music.pause()
                continue
            time.sleep(1)

    except Exception as e:
        print(f"Error while playing the song: {e}")

def pause_song():
    """Pause the song."""
    global pause_playing
    pause_playing = True
    print("Song paused.")

def resume_song():
    """Resume the song."""
    global pause_playing
    pause_playing = False
    pygame.mixer.music.unpause()
    print("Song resumed.")

def main():
    """Main client program."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connected to the server.")

        while True:
            print("\nMenu:")
            print("\n1. List Playlists")
            print("2. Select Playlist and View Songs")
            print("3. Select Song and Play")
            print("4. Get Lyrics")
            print("5. Pause/Resume Song")
            print("6. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                list_playlists(client_socket)
            elif choice == "2":
                playlists = list_playlists(client_socket)
                playlist_index = int(input("Select playlist: ")) - 1
                list_songs(client_socket, playlists[playlist_index])
            elif choice == "3":
                playlists = list_playlists(client_socket)
                playlist_index = int(input("Select playlist: ")) - 1
                songs = list_songs(client_socket, playlists[playlist_index])
                song_index = int(input("Select song: ")) - 1
                play_song(client_socket, playlists[playlist_index], songs[song_index])
            elif choice == "4":
                playlists = list_playlists(client_socket)
                playlist_index = int(input("Select playlist: ")) - 1
                songs = list_songs(client_socket, playlists[playlist_index])
                song_index = int(input("Select song: ")) - 1
                get_lyrics(client_socket, playlists[playlist_index], songs[song_index])
            elif choice == "5":
                action = input("Enter 'p' to pause or 'r' to resume: ")
                if action == 'p':
                    pause_song()
                elif action == 'r':
                    resume_song()
                else:
                    print("Invalid action")
            elif choice == "6":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
