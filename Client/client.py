import socket
import sys
from os.path import exists as file_exists
import threading
import time
# Threaded Client

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
input_file = sys.argv[1]
# print(input_file)
cache = {}

# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "127.0.0.1"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def send(method, msg, file_name):
    # print(threading.current_thread().ident, file_name)
    message = msg.encode(FORMAT)
    if message in cache:
        print("Getting From Cache...")
        body = cache[message]
    else:
        print("Sending Request...")
        client.send(message)
        body = client.recv(8192).decode(FORMAT)
        cache[message] = body
    response, contents = body.rsplit("\r\n\r\n", 1)
    if method == "GET" and "200 OK" in response:
        get_file = open(file_name[1:].replace('/', '.'), "w")
        get_file.write(contents)
        get_file.write("\r\n")
        get_file.close()
    print(message)
    print(threading.current_thread().ident, file_name, '\n', response, '\n')


def start(request_input):
    entries = request_input.split(' ')
    method = entries[0]
    file_name = entries[1]
    # print(threading.current_thread().ident, file_name)
    host_name = entries[2]
    if host_name == "localhost" or host_name == "192.168.56.1" or host_name == "127.0.0.1":
        SERVER = socket.gethostbyname(socket.gethostname())
    else:
        SERVER = host_name
    if len(entries) == 4:
        PORT = entries[3]
    else:
        PORT = 80
    global ADDR
    ADDR = (SERVER, int(PORT))

    request = ""
    if host_name == "localhost" or host_name == "192.168.56.1" or host_name == "127.0.0.1":
        request = method + " " + file_name + " " + "HTTP/1.1\r\n" + "HOST: " + host_name + ":" + PORT + "\r\n\r\n"
        # if method == "GET":
        if method == "POST":
            # request = method + " " + file_name + " " + "HTTP/1.0\r\n" + "HOST: " + host_name + ":" + PORT + "\r\n\r\n"
            if file_exists(file_name[1:]):
                t = open(file_name[1:], "r")
                for v in t.readlines():
                    request += v
                t.close()
    else:
        if method == "GET":
            request = method + " " + file_name + " " + "HTTP/1.1\r\n" + "HOST: " + host_name + "\r\n\r\n"
        elif method == "POST":
            request = method + " / " + "HTTP/1.1\r\n" + "HOST: " + host_name + "\r\n\r\n"
            if file_exists(file_name[1:]):
                t = open(file_name[1:], "r")
                for v in t.readlines():
                    request += v
                t.close()
    request += "\r\n"

    print(threading.current_thread().ident, file_name, '\n', request)
    try:
        send(method, request, file_name)
    except:
        connect()
        send(method, request, file_name)


def connect():
    try:
        print("New Connection...")
        client.connect(ADDR)
    except:
        reconnect()


def reconnect():
    try:
        global client
        print("Reconnecting...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
    except:
        reconnect()


# while True:
# print("Enter Request: ")
# request_input = input()
if file_exists(input_file):
    t = open(input_file, "r")
    for line in t.readlines():
        # print(line)
        thread = threading.Thread(target=start, args=(line,))
        thread.start()
        # start(line)
        time.sleep(1)
    t.close()
else:
    print("Invalid Input File")
    # if request_input == "Close":
    #     break

    # start()

# send(DISCONNECT_MESSAGE)
# print(cache)
# print("[CONNECTION CLOSED]")