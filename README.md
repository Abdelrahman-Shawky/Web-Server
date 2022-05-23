# Web-Server
Multi-threaded Web Server and Simple Client using socket programming implemented in python

## Description
- Program can run on any available port on the system.
- Multiple requests can be handled by the server at the same time.
- Allows for persistent connections.
- Supports pipelining of client requests
- Handles both GET & POST requests.
- Supports HTTP/1.0 and HHTP/1.1.
- Responds with "HTTP/1.X 200 OK" if request is fulfilled
- Responds with "HTTP/1.X 404 NOT FOUND" if request is not fulfilled.

## Multi-Threaded Web Server
- Accept incoming connection requests
- If GET request then looks up the name of the requested file in the current server directory.
- If POST request then saves body of packet in a new file.
- If request is fulfilled then "200 OK" message is sent.
- If request is not fulfilled then "404 NOT FOUND" message is sent.

#### Sample Response

    HTTP/1.0 200 OK\r\n 
    then in case of GET command only: 
    {data, data, ...., data}\r\n
    
    HTTP/1.0 404 Not Found\r\n
    
#### Server Side Pseudo Code
    while true:
      - Listen for connections 
      - Accept new connection from incoming client and delegate it to worker thread/process 
      - Parse HTTP/1.0 request and determine the command (GET or POST) 
      - Determine if target file exists (in case of GET) and return error otherwise
      - Transmit contents of the file (reads from the file and writes on the socket) (in case of GET) 
      - Close the connection
    end while 
   
## HTTP Web Client
- Read and parse commands from input file.
- Client opens a connection to an HTTP server on the specified host.
- If GET request then displays the file and stores it in the local directory.
- Shuts down when reaching the end of file.
- Supports caching functionality

#### Sample Request
    
    GET file-name host-name (port-number) 
    POST file-name host-name (port-number)
    
#### Client Side Pseudo Code
    while more operation exists do:
      - Create a TCP connection with the server 
      - Wait for permission from the server 
      - Send next requests to the server 
      - Receives data from the server (in case of GET) or sends data (in case of POST) 
      - Close the connection
    end while
    
## How To Run
1. Navigate to project directory
2. Run server side ```py server.py```
3. Run client side ```py client.py```
    
  
    
