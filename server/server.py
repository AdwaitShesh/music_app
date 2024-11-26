import socket
import os
from threading import Thread

# Directory to store playlists
PLAYLIST_DIR = r"D:\SPIT\SPITTE\DC\music_app\server\playlists"
DOWNLOAD_DIR = r"D:\SPIT\SPITTE\DC\music_app\server\downloads"

# Function to handle client requests
def handle_client(client_socket):
    while True:
        try:
            request = client_socket.recv(4096).decode()

            # Request to list playlists
            if request.startswith("LIST_PLAYLISTS"):
                playlists = os.listdir(PLAYLIST_DIR)
                response = "|".join(playlists)
                client_socket.send(response.encode())

            # Request to get songs in a playlist
            elif request.startswith("GET_SONGS"):
                playlist_name = request.split("|")[1]
                songs = os.listdir(os.path.join(PLAYLIST_DIR, playlist_name))
                response = "|".join(songs)
                client_socket.send(response.encode())

            # Request to get lyrics of a song
            elif request.startswith("GET_LYRICS"):
                playlist_name, song_name = request.split("|")[1], request.split("|")[2]
                song_path = os.path.join(PLAYLIST_DIR, playlist_name, song_name.replace(".mp3", ".txt"))
                try:
                    with open(song_path, "r") as file:
                        response = file.read()
                    client_socket.send(response.encode())
                except FileNotFoundError:
                    client_socket.send(b"ERROR: Lyrics not found.")

            # Request to play a song
            elif request.startswith("PLAY_SONG"):
                playlist_name, song_name = request.split("|")[1], request.split("|")[2]
                song_path = os.path.join(PLAYLIST_DIR, playlist_name, song_name)
                if os.path.exists(song_path):
                    with open(song_path, "rb") as song_file:
                        data = song_file.read(4096)
                        while data:
                            client_socket.send(data)
                            data = song_file.read(4096)
                    client_socket.send(b"EOF")
                else:
                    client_socket.send(b"ERROR: Song not found.")
        except Exception as e:
            print(f"Error handling client request: {e}")
            break

    client_socket.close()

def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server started on {ip}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")
        thread = Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 8080
    start_server(ip, port)
