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
# server.settimeout(10) # 10s of persistent connection
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    while connected:
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg_length:  # First empty message
        #     msg_length = int(msg_length)
        # try:
        # server.settimeout(10)

        msg = conn.recv(2048).decode(FORMAT)
        if len(msg) != 0:  # Avoid receiving empty msg
            # server.settimeout(None)
            # except socket.timeout:
            #     break

            # if msg == DISCONNECT_MESSAGE:
            #     break
            #     connected = False
            method_string, headers, body = parse_request(msg)
            # if headers["Connection"] is not None and headers["Connection"] == "close":  # Non-persistent
            #     connected = False
            response, http_version = select_method(method_string, body)
            print(f"[{addr}]")
            print(msg, "\n")
            # print(response)
            conn.send(response.encode(FORMAT))
            # connected = False
            if http_version == 'HTTP/1.0':
                break
            elif http_version == 'HTTP/1.1':
                pass
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
    # _, file = url.split("/", 1)
    # file_name, extension = file.rsplit(".", 1)
    # response = ""
    # if file_exists(file):
    #     response += http_version + " 200 OK\r\n"
    #     read_file = open(file, "r")
    #     post_file_name = file_name + "_POST." + extension
    #     post_file = open(post_file_name, "w")
    #     for line in read_file.readlines():
    #         response += line
    #         post_file.write(line)
    #     read_file.close()
    #     post_file.close()
    # else:
    #     response += http_version + " 404 Not Found\r\n"
    # body = body.split("\r\n")
    # print("2", body)
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
    # os.environ['NO_PROXY'] = '127.0.0.1'
    # r = requests.get('http://localhost:5050/Server/test.txt')
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
    # body = ""
    header, body = request.split('\r\n\r\n', 1)
    # request = request.split('\r\n\r\n', 1)
    # print("dehk", request)
    method_string, headers = header.split('\r\n', 1)
    # if len(request) == 2:
    #     body = request[1]
    # print("1", body)

    # construct a message from the request string
    message = email.message_from_file(StringIO(headers))

    # construct a dictionary containing the headers
    headers = dict(message.items())

    # pretty-print the dictionary of headers
    # pprint.pprint(headers, width=160)
    return method_string, headers, body


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()







