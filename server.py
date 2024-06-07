import socket
import threading
import asyncio
import websockets
import sympy as sp
import math

# Global variables
clients = set()
broadcasting = False

# Function to handle receiving messages from the client socket
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            print(message)
        except Exception as e:
            print(f"[ERROR] {e}")
            break

# Function to calculate trigonometric function value
def calculate_trigonometric(trig_function, angle):
    try:
        angle_radians = math.radians(angle)
        if trig_function == 'sin':
            return math.sin(angle_radians)
        elif trig_function == 'cos':
            return math.cos(angle_radians)
        elif trig_function == 'tan':
            return math.tan(angle_radians)
        elif trig_function == 'cot':
            return 1 / math.tan(angle_radians)
        elif trig_function == 'sec':
            return 1 / math.cos(angle_radians)
        elif trig_function == 'cosec':
            return 1 / math.sin(angle_radians)
        else:
            return None
    except Exception as e:
        return f"Error: {e}"

# Function to handle menu choice selection by the client
def menu_choice(client_socket):
    while True:
        print("\nMenu:")
        print("1. Turunan Orde Pertama")
        print("2. Integral Orde Pertama")
        print("3. Fungsi Trigonometri (sin, cos, tan, cot, sec, cosec)")
        print("4. Operasi Matematika Dasar (tambah, kurang, kali, bagi)")
        print("5. Turunan Orde Kedua")
        print("6. Turunan Orde Ketiga")
        print("7. Turunan Orde Keempat")
        print("8. Integral Orde Kedua")
        print("9. Integral Orde Ketiga")
        print("10. Integral Orde Keempat")
        print("11. Keluar")

        choice = input("Pilih opsi (1-11): ")

        if choice == '11':
            client_socket.close()
            break

        if choice not in [str(i) for i in range(1, 12)]:
            print("Pilihan tidak valid.")
            continue

        if choice == '3':
            trig_function = input("Masukkan fungsi trigonometri (sin, cos, tan, cot, sec, cosec): ").lower()
            angle = float(input("Masukkan sudut dalam derajat: "))
            result = calculate_trigonometric(trig_function, angle)
            message = f"{trig_function}({angle}) = {result}"
            print(message)
            client_socket.send(f"3:{trig_function},{angle}".encode("utf-8"))
        else:
            expression = input("Masukkan ekspresi matematika: ")
            client_socket.send(f"{choice}:{expression}".encode("utf-8"))

# Function to handle each client connection
async def handle_client(websocket, path):
    global broadcasting
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")

            # Check if the message is a broadcasting command
            if message.startswith("Broadcasting:"):
                broadcasting = message.split(":")[1].strip() == "1"
                print(f"Broadcasting set to: {broadcasting}")
                continue

            # Split the message into menu choice and expression
            menu_choice, expression = message.split(":")
            menu_choice = int(menu_choice)

            # Perform calculations based on menu choice
            result = None
            if menu_choice == 1:
                result = calculate_derivative(expression, 1)
            elif menu_choice == 2:
                result = calculate_integral(expression, 1)
            elif menu_choice == 3:
                result = calculate_trigonometric(expression)
            elif menu_choice == 4:
                result = calculate_basic_math(expression)
            elif menu_choice in [5, 6, 7]:
                result = calculate_derivative(expression, menu_choice - 4)
            elif menu_choice in [8, 9, 10]:
                result = calculate_integral(expression, menu_choice - 7)
            else:
                result = "Invalid menu choice"

            # Prepare message to send
            message_to_send = f"Result of {expression}: {result}"

            # Broadcast the message if broadcasting mode is enabled
            if broadcasting:
                await broadcast(message_to_send)
            else:
                await websocket.send(message_to_send)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        clients.remove(websocket)

# Function to calculate derivative using sympy
def calculate_derivative(expression, order):
    try:
        x = sp.symbols('x')
        expr = sp.sympify(expression)
        derivative = sp.diff(expr, x, order)
        return str(derivative)
    except Exception as e:
        return f"Error: {e}"

# Function to calculate integral using sympy
def calculate_integral(expression, order):
    try:
        x = sp.symbols('x')
        expr = sp.sympify(expression)
        integral = expr
        for _ in range(order):
            integral = sp.integrate(integral, x)
        return str(integral)
    except Exception as e:
        return f"Error: {e}"

# Function to calculate basic math operations
def calculate_basic_math(expression):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# Function to broadcast messages to all connected clients
async def broadcast(message):
    if clients:
        await asyncio.gather(*(client.send(message) for client in clients))

# Start the WebSocket server
async def main_async():
    server = await websockets.serve(handle_client, "0.0.0.0", 11008)
    async with server:
        await asyncio.Future()  # Run forever

# Main function to initialize the client socket and start the menu choice loop
def main():
    # Start the event loop for the WebSocket server in a separate thread
    server_thread = threading.Thread(target=lambda: asyncio.run(main_async()))
    server_thread.start()

    # Initialize the client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the client to the server
    client.connect(("localhost", 11008))  # Use 'localhost' if running on the same machine

    # Start a thread to handle receiving messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # Start the menu choice loop
    menu_choice(client)

if __name__ == "__main__":
    main()
