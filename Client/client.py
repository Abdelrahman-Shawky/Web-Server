import socket
from os.path import exists as file_exists
# Threaded Client

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "127.0.0.1"


def send(method, msg, client, file_name):

    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    client.send(message)
    print("I am sending.....")
    body = client.recv(8192).decode(FORMAT)
    response, contents = body.rsplit("\r\n\r\n", 1)
    if method == "GET" and "200 OK" in response:
        get_file = open(file_name[1:].replace('/', '.'), "w")
        get_file.write(contents)
        # for line in body:
        #     get_file.write(line)
        get_file.write("\r\n")
        get_file.close()
    print(response)
    # print(client.recv(2048).decode(FORMAT))


def start():
    # print("Enter Request: ")
    # request_input = input()
    entries = request_input.split(' ')
    method = entries[0]
    file_name = entries[1]
    host_name = entries[2]
    if host_name == "localhost" or host_name == "192.168.56.1" or host_name == "127.0.0.1":
        SERVER = socket.gethostbyname(socket.gethostname())
    else:
        SERVER = host_name
    if len(entries) == 4:
        PORT = entries[3]
    else:
        PORT = 80
    ADDR = (SERVER, int(PORT))

    # send('GET /test.txt HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\nAccept-Encoding: gzip, deflate, sdch\r\nAccept-Language: en-US,en;q=0.8')
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
        request += "\r\n"
    else:
        if method == "GET":
            request = method + " " + file_name + " " + "HTTP/1.0\r\n" + "HOST: " + host_name + "\r\n\r\n"
        elif method == "POST":
            request = method + " / " + "HTTP/1.0\r\n" + "HOST: " + host_name + "\r\n\r\n"
    print(request)
    # if still connected send, else connect again and send
    # client.connect(ADDR)
    # send(method, request,client, file_name)
    # client.close()

    try:
        send(method, request, client, file_name)
    except socket.error:
        client.connect(ADDR)
        print("new  connection.....")
        send(method, request, client, file_name)

    # client.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    print("Enter Request: ")
    request_input = input()
    if request_input == "Close":
        break
    start()

# send(DISCONNECT_MESSAGE)
print("[CONNECTION CLOSED]")