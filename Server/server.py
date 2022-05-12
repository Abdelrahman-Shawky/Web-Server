# import socket
#
# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
#
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print(f"Connected by {addr}")
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             conn.sendall(data)

# multiconn-server.py

# import sys
# import socket
# import selectors
# import types
#
#
# def accept_wrapper(sock):
#     conn, addr = sock.accept()  # Should be ready to read
#     print(f"Accepted connection from {addr}")
#     conn.setblocking(False)
#     data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
#     events = selectors.EVENT_READ | selectors.EVENT_WRITE
#     sel.register(conn, events, data=data)
#
#
# def service_connection(key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         if recv_data:
#             data.outb += recv_data
#         else:
#             print(f"Closing connection to {data.addr}")
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if data.outb:
#             print(f"Echoing {data.outb!r} to {data.addr}")
#             sent = sock.send(data.outb)  # Should be ready to write
#             data.outb = data.outb[sent:]
#
#
# sel = selectors.DefaultSelector()
#
# # ...
# # HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
# # PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
#
# host, port = sys.argv[1], int(sys.argv[2])
# lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# lsock.bind((host, port))
# lsock.listen()
# print(f"Listening on {(host, port)}")
# lsock.setblocking(False)
# sel.register(lsock, selectors.EVENT_READ, data=None)
#
# try:
#     while True:
#         events = sel.select(timeout=None)
#         for key, mask in events:
#             if key.data is None:
#                 accept_wrapper(key.fileobj)
#             else:
#                 service_connection(key, mask)
# except KeyboardInterrupt:
#     print("Caught keyboard interrupt, exiting")
# finally:
#     sel.close()


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
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    while connected:
        # msg_length = conn.recv(HEADER).decode(FORMAT)
        # if msg_length:  # First empty message
        #     msg_length = int(msg_length)
        msg = conn.recv(2048).decode(FORMAT)
        # if msg == DISCONNECT_MESSAGE:
        #     break
            # connected = False
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
    print("1", body)

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







