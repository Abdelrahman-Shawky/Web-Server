import socket
import threading
import email
import pprint
import requests
from io import StringIO
from os.path import exists as file_exists
import os


PORT = 5050
# SERVER = "127.0.0.1"
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)
HEADER = 64  # Message default length
FORMAT = 'utf-8' # Decode format
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    while connected:
        try:
            msg = conn.recv(2048).decode(FORMAT)
        except:
            break
        if len(msg) != 0:  # Avoid receiving empty msg
            method_string, headers, body = parse_request(msg)
            # if headers["Connection"] is not None and headers["Connection"] == "close":  # Non-persistent
            #     connected = False
            response, http_version = select_method(method_string, body)
            print(f"[{addr}]")
            print(msg, "\n")
            conn.send(response.encode(FORMAT))
            if http_version == 'HTTP/1.0':
                break
            elif http_version == 'HTTP/1.1':
                pass
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
    print(f"[CONNECTION CLOSED]")


def select_method(method_string, body):
    method, url, http_version = method_string.split(' ', 2)
    if method == "POST":
        return post_request(url, http_version, body)
    elif method == "GET":
        return get_request(url, http_version)
    else:
        pass


def post_request(url, http_version, body):
    _, file = url.split("/", 1)
    if file != '':
        file_name, extension = file.rsplit(".", 1)
        file_name += "_posted"
        file = file_name + "." + extension
    else:
        file = "mizo.txt"
    post_file = open(file, "w")
    post_file.write(body)
    # for line in body:
    #     post_file.write(line)
    post_file.write("\r\n")
    post_file.close()

    response = http_version + " 200 OK\r\n\r\n"
    return response, http_version


def get_request(url, http_version):
    _, file = url.split("/", 1)
    response = ""
    if file_exists(file):
        response += http_version + " 200 OK\r\n\r\n"
        t = open(file, "r")
        for v in t.readlines():
            response += v
        t.close()
    else:
        response += http_version + " 404 Not Found\r\n\r\n"
    return response, http_version


def parse_request(request):
    print(request)
    # pop the first line so we only process headers
    header, body = request.split('\r\n\r\n', 1)
    method_string, headers = header.split('\r\n', 1)
    # construct a message from the request string
    message = email.message_from_file(StringIO(headers))
    # construct a dictionary containing the headers
    headers = dict(message.items())
    return method_string, headers, body


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        conn.settimeout(10)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()







