import socket

def main():
    host = '10.169.13.13'
    port = 11008

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        expression = input("Enter an expression: ")
        if expression.lower() == 'exit':
            break
        client_socket.send(expression.encode('utf-8'))
        result = client_socket.recv(1024).decode('utf-8')
        print("Result:", result)

    client_socket.close()

if __name__ == "__main__":
    main()
