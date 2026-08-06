from socket import socket, AF_INET, SOCK_STREAM
cache = {}  #start with an empty dictionary

def main():
    PORT = 3128
    BUFFER = 1024

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("", PORT))
    server_socket.listen(1)

    print("Proxy Server Ready...")

    while True:
        connection_socket, addr = server_socket.accept()

        client_message = connection_socket.recv(BUFFER).decode()
        if not client_message:
                    connection_socket.close()
                    continue

        request_line = client_message.split("\r\n")[0]
        request_parts = request_line.split(" ")
        requested_object = request_parts[1]

        if requested_object in cache:
              print("Object found in cache", requested_object)
              connection_socket.send(cache[requested_object]) #send the existing object from cache

        else:
              print("Object not found in cache")

              proxy_socket = socket(AF_INET, SOCK_STREAM)
              #now proxy server connects to the original web server to send request

              proxy_socket.connect(("localhost", 8080)) 
              proxy_socket.sendall(client_message.encode()) #forwarding the client request

              origin_response = proxy_socket.recv(BUFFER)

              cache[requested_object] = origin_response #storing the response in cache for future use
              connection_socket.sendall(origin_response) 

              proxy_socket.close()
        
        connection_socket.close()

if __name__ == "__main__":
    main()