from flask import Flask, render_template, request
import threading
import socket
import sympy as sp

app = Flask(__name__)

clients = []
lock = threading.Lock()

def handle_client(client_socket, client_address):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            result = evaluate_expression(data)
            broadcast_data(result, client_socket)
        except Exception as e:
            print(f"Error with client {client_address}: {e}")
            break
    with lock:
        clients.remove(client_socket)
    client_socket.close()

def broadcast_data(data, sender_socket):
    with lock:
        for client in clients:
            if client != sender_socket:
                client.send(data.encode('utf-8'))

def evaluate_expression(expression):
    x = sp.symbols('x')
    try:
        result = str(sp.simplify(expression))
    except Exception as e:
        result = str(e)
    return result

def start_socket_server():
    host = '0.0.0.0'
    port = 11008
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(3)
    print(f"Socket server running on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        with lock:
            clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.form['expression']
    result = evaluate_expression(expression)
    with lock:
        for client in clients:
            client.send(result.encode('utf-8'))
    return result

if __name__ == "__main__":
    threading.Thread(target=start_socket_server).start()
    app.run(host='0.0.0.0', port=5000)
