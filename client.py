# import socket
#
# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server
#
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b"Hello, world") # Ensures all bytes have been sent
#     data = s.recv(1024)
#
# print(f"Received {data!r}")



# import sys
# import socket
# import selectors
# import types
#
# sel = selectors.DefaultSelector()
# messages = [b"Message 1 from client.", b"Message 2 from client."]
#
#
# def start_connections(host, port, num_conns):
#     server_addr = (host, port)
#     for i in range(0, num_conns):
#         connid = i + 1
#         print(f"Starting connection {connid} to {server_addr}")
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setblocking(False)
#         sock.connect_ex(server_addr)
#         events = selectors.EVENT_READ | selectors.EVENT_WRITE
#         data = types.SimpleNamespace(
#             connid=connid,
#             msg_total=sum(len(m) for m in messages),
#             recv_total=0,
#             messages=messages.copy(),
#             outb=b"",
#         )
#         sel.register(sock, events, data=data)
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
#             print(f"Received {recv_data!r} from connection {data.connid}")
#             data.recv_total += len(recv_data)
#     if not recv_data or data.recv_total == data.msg_total:
#         print(f"Closing connection {data.connid}")
#         sel.unregister(sock)
#         sock.close()
#     if mask & selectors.EVENT_WRITE:
#         if not data.outb and data.messages:
#             data.outb = data.messages.pop(0)
#     if data.outb:
#         print(f"Sending {data.outb!r} to connection {data.connid}")
#         sent = sock.send(data.outb)  # Should be ready to write
#         data.outb = data.outb[sent:]
#
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
from os.path import exists as file_exists


HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

print("Enter Request: ")
request_input = input()
entries = request_input.split(' ')
method = entries[0]
file_name = entries[1]
host_name = entries[2]
if host_name == "localhost":
    SERVER = socket.gethostbyname(socket.gethostname())
else:
    SERVER = host_name
if len(entries) == 4:
    PORT = entries[3]
else:
    PORT = 80



# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "127.0.0.1"
ADDR = (SERVER, int(PORT))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    client.send(message)
    body = client.recv(8192).decode(FORMAT)
    _, contents = body.rsplit("\r\n", 1)
    get_file = open(file_name[1:].replace('/', '.'), "w")
    get_file.write(contents)
    # for line in body:
    #     get_file.write(line)
    get_file.write("\r\n")
    get_file.close()
    print(body)
    # print(client.recv(2048).decode(FORMAT))


# send('GET /test.txt HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en-US,en;q=0.8')
if host_name == "localhost":
    request = method + " " + file_name + " " + "HTTP/1.0\r\n" + "HOST: " + host_name + ":" + PORT + "\r\n\r\n"
    # if method == "GET":
    if method == "POST":
        # request = method + " " + file_name + " " + "HTTP/1.0\r\n" + "HOST: " + host_name + ":" + PORT + "\r\n\r\n"
        if file_exists(file_name):
            t = open(file_name, "r")
            for v in t.readlines():
                request += v
            t.close()
    request += "\r\n"

else:
    if method == "GET":
        request = method + " " + file_name + " " + "HTTP/1.0\r\n" + "HOST: " + host_name + "\r\n\r\n"
    elif method == "POST":
        request = method + " / " + "HTTP/1.0\r\n" + "HOST: " + host_name + "\r\n\r\n"

print(request)
send(request)




# send(DISCONNECT_MESSAGE)
print("[CONNECTION CLOSED]")
