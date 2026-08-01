from socket import socket, AF_INET, SOCK_STREAM
import os
from datetime import datetime, timezone

def main():
    PORT = 8080
    BUFFER = 1024

    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("", PORT))
    server_socket.listen(1)

    print("Server Ready...")
    while True:
        connection_socket, addr = server_socket.accept()

        client_message = connection_socket.recv(BUFFER).decode()
        if not client_message:
            connection_socket.close()
            continue

        print("Client Message: \n", client_message)

        request_line = client_message.split("\r\n")[0]
        request_parts = request_line.split(" ")
        filename = request_parts[1][1:]
        http_version = request_parts[2].strip()

        if http_version not in ["HTTP/1.0", "HTTP/1.1"]:
            error_header = f" {http_version} 505 HTTP Version Not Supported\r\n\r\n"
            connection_socket.send(error_header.encode())
            connection_socket.close()
            continue

        if not os.path.exists(filename):
            error_header = "HTTP/1.1 404 Not Found\r\n\r\n"
            error_body = "<html><body><h1>404 Not Found</h1></body></html>"
            connection_socket.send(error_header.encode())
            connection_socket.send(error_body.encode())

        elif not os.access(filename, os.R_OK):
            error_header = "HTTP/1.1 403 Forbidden\r\n\r\n"
            error_body = "<html><body><h1>403 Forbidden</h1></body></html>"
            connection_socket.send(error_header.encode())
            connection_socket.send(error_body.encode())

        else:
            with open(file=filename, mode="rb") as f:
                file_data = f.read()

            send_file = True

            if "If-Modified-Since:" in client_message:
                headers_list = client_message.split("\r\n")
                headers_dict = {}

                for item in headers_list[1:]:
                    if ":" not in item:
                        continue

                    key_value_pair = item.split(":", 1)
                    key = key_value_pair[0].strip()
                    value = key_value_pair[1].strip()
                    headers_dict[key] = value

                if "If-Modified-Since" in headers_dict:
                    modified_since = headers_dict["If-Modified-Since"]
                    client_date = datetime.strptime(
                        modified_since,
                        "%a, %d %b %Y %H:%M:%S GMT"
                    ).replace(tzinfo=timezone.utc)

                    file_modified_date = datetime.fromtimestamp(
                        os.path.getmtime(filename),
                        timezone.utc
                    )

                    if file_modified_date <= client_date:
                        error_header = "HTTP/1.1 304 Not Modified\r\n\r\n"
                        connection_socket.send(error_header.encode())
                        send_file = False

            if send_file:
                success_header = "HTTP/1.1 200 OK\r\n\r\n"
                connection_socket.send(success_header.encode())
                connection_socket.send(file_data)

        connection_socket.close()

if __name__ == "__main__":
    main()