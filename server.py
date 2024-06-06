from flask import Flask, request, jsonify
import socket
import threading
import sympy as sp

app = Flask(__name__)

clients = []
lock = threading.Lock()

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            broadcast_data(data)
            result = evaluate_expression(data)
            client_socket.send(result.encode('utf-8'))
        except Exception as e:
            print("Error:", e)
            break
    client_socket.close()
    with lock:
        clients.remove(client_socket)

def broadcast_data(data):
    with lock:
        for client in clients:
            client.send(data.encode('utf-8'))

def evaluate_expression(expression):
    x = sp.symbols('x')
    try:
        result = str(sp.simplify(expression))
    except Exception as e:
        result = str(e)
    return result

@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.json['expression']
    result = evaluate_expression(expression)
    broadcast_data(expression)
    return jsonify(result=result)

def start_server():
    host = '0.0.0.0'
    port = 11008

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(3)

    print("Server is running on {}:{}".format(host, port))

    while True:
        client_socket, client_addr = server_socket.accept()
        print("Connection from:", client_addr)
        with lock:
            clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    app.run(host='0.0.0.0', port=11008)
