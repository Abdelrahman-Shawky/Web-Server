import socket
import threading
from threading import Lock
import email
from heapq import heapify, heappush, heappop
import pprint
import requests
from io import StringIO
from os.path import exists as file_exists
import time

import os

PORT = 5050
# SERVER = "127.0.0.1"
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)
HEADER = 64  # Message default length
FORMAT = 'utf-8'  # Decode format
DISCONNECT_MESSAGE = "!DISCONNECT"
active_connections = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(ADDR)
queue = []
heap = []
heapify(heap)
time_dict = {}
mutex = Lock()
print_mutex = Lock()


def receive_message_thread(conn, addr):
    connected = True
    # conn.settimeout(30)
    while connected:
        try:
            msg = conn.recv(2048).decode(FORMAT)
            current_time = time.time()
            time_dict[threading.current_thread().ident] = current_time
            mutex.acquire()
            heappush(heap, current_time)
            mutex.release()
        except:
            break
        if len(msg) != 0:  # Avoid receiving empty msg
            method_string, headers, body = parse_request(msg)
            # if headers["Connection"] is not None and headers["Connection"] == "close":  # Non-persistent
            #     connected = False
            response, http_version = select_method(method_string, body)
            # dict[msg] = response
            thread = threading.Thread(target=receive_message_thread, args=(conn, addr))
            thread.start()

            def check():
                mutex.acquire()
                element = heappop(heap)
                if time_dict[threading.current_thread().ident] != element:
                    heappush(heap, element)
                else:
                    mutex.release()
                    return True
                # heappush(heap, element)
                mutex.release()
                return False

            while not check():
                pass
            print_mutex.acquire()
            print(f"[{addr}]", threading.current_thread().ident, time_dict[threading.current_thread().ident], '\n', msg, response)
            print_mutex.release()
            # print(msg)
            conn.send(response.encode(FORMAT))
            # mutex.acquire()
            # heappop(heap)
            # mutex.release()


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    global time_dict
    global heap
    # myTime = time.time()
    while connected:
        try:
            # conn.settimeout(10)
            msg = conn.recv(2048).decode(FORMAT)
            # print("mizo1")
            if len(msg)==0:
                # print("mizo2")
                period = time.time()-current_time
                # print(period)
                if period > 10:
                    # time_dict = {}
                    # heap = []
                    break
            else:
                # print("mizo3")
                current_time = time.time()
                time_dict[threading.current_thread().ident] = current_time
                mutex.acquire()
                heappush(heap, current_time)
                mutex.release()
        except:
            break
        if len(msg) != 0:  # Avoid receiving empty msg
            # print("mizo4")
            method_string, headers, body = parse_request(msg)
            # if headers["Connection"] is not None and headers["Connection"] == "close":  # Non-persistent
            #     connected = False
            response, http_version = select_method(method_string, body)
            # dict[msg] = response
            if http_version == 'HTTP/1.1':
                thread = threading.Thread(target=receive_message_thread, args=(conn, addr))
                thread.start()
            if threading.current_thread().name == "Main":
                # time.sleep(15)
                # print("mizo5")

                def check():
                    mutex.acquire()
                    element = heappop(heap)
                    if time_dict[threading.current_thread().ident] != element:
                        heappush(heap, element)
                    else:
                        mutex.release()
                        return True
                    # heappush(heap, element)
                    mutex.release()
                    return False

                while not check():
                    pass
                # print("mizo6")
                print_mutex.acquire()
                print(f"[{addr}]", threading.current_thread().ident, time_dict[threading.current_thread().ident], '\n', msg, response)
                print_mutex.release()
                # print(msg)
                conn.send(response.encode(FORMAT))
                # mutex.acquire()
                # heappop(heap)
                # mutex.release()
                if http_version == 'HTTP/1.0':
                    break
                # conn.close()
    if threading.current_thread().name == "Main":
        conn.close()
        time_dict = {}
        heap = []
        print(f"[CONNECTION CLOSED]")
        global active_connections
        active_connections -= 1
        print(f"[ACTIVE CONNECTIONS] {active_connections}")


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
        # conn.settimeout(10)
        # conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        # conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
        # conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT,5)
        # conn.setblocking(0)
        thread = threading.Thread(target=handle_client, name="Main", args=(conn, addr))
        thread.start()
        global active_connections
        active_connections += 1
        print(f"[ACTIVE CONNECTIONS] {active_connections}")


print("[STARTING] Server is starting...")
start()
