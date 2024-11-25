import socket
import threading
import os
from lamport import LamportClock
from weighted_round_robin import WeightedRoundRobin
from playsound import playsound

# Initialize Lamport Clock
lamport_clock = LamportClock()

# Playlists directory
PLAYLIST_DIR = r"D:\SPIT\SPITTE\DC\music_app\server\playlists"

# Weighted Round Robin for load balancing
servers = [("127.0.0.1", 8080, 3), ("127.0.0.1", 8081, 2)]
load_balancer = WeightedRoundRobin(servers)

def handle_client(client_socket, address):
    global lamport_clock
    print(f"Connection established with {address}")

    while True:
        try:
            # Receive request
            request = client_socket.recv(1024).decode()
            if not request:
                break

            # Process Lamport clock timestamp
            lamport_clock.receive_event(int(request.split('|')[-1]))

            # Command handlers
            if request.startswith("LIST_PLAYLISTS"):
                playlists = os.listdir(PLAYLIST_DIR)
                response = "|".join(playlists)

            elif request.startswith("GET_SONGS"):
                try:
                    playlist = request.split("|")[1]
                    songs = os.listdir(os.path.join(PLAYLIST_DIR, playlist))
                    response = "|".join(songs)
                except FileNotFoundError:
                    response = "ERROR: Playlist not found."

            elif request.startswith("GET_LYRICS"):
                try:
                    parts = request.split("|")
                    if len(parts) < 3:
                        response = "ERROR: Invalid command format for GET_LYRICS."
                    else:
                        playlist, song = parts[1], parts[2]
                        lyrics_path = os.path.join(PLAYLIST_DIR, playlist, song.replace(".mp3", ".txt"))
                        if os.path.exists(lyrics_path):
                            with open(lyrics_path, 'r') as file:
                                response = file.read()
                        else:
                            response = "ERROR: Lyrics file not found."
                except Exception as e:
                    response = f"ERROR: {str(e)}"

            elif request.startswith("PLAY_SONG"):
                try:
                    parts = request.split("|")
                    if len(parts) < 3:
                        response = "ERROR: Invalid command format for PLAY_SONG."
                    else:
                        playlist, song = parts[1], parts[2]
                        song_path = os.path.join(PLAYLIST_DIR, playlist, song)
                        if os.path.exists(song_path):
                            # Play the song
                            response = f"Playing {song}..."
                            threading.Thread(target=playsound, args=(song_path,)).start()
                        else:
                            response = "ERROR: Song file not found."
                except Exception as e:
                    response = f"ERROR: {str(e)}"

            elif request.startswith("GET_LAMPORT"):
                response = str(lamport_clock.get_time())

            else:
                response = "INVALID_COMMAND"

            # Increment Lamport clock and send response
            lamport_clock.increment()
            client_socket.send(f"{response}|{lamport_clock.get_time()}".encode())

        except Exception as e:
            print(f"Error handling client {address}: {e}")
            break

    client_socket.close()

def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server listening on {ip}:{port}")

    while True:
        try:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.start()
        except Exception as e:
            print(f"Error accepting new connection: {e}")

if __name__ == "__main__":
    # Select server using weighted round robin
    ip, port = load_balancer.get_server()
    threading.Thread(target=start_server, args=(ip, port)).start()
