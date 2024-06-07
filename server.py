from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    mode = request.form['mode']
    result = 0

    if mode == 'normal':
        expression = request.form['expression']
        try:
            result = eval(expression)
        except:
            result = 'Error'
    elif mode == 'trigonometry':
        angle = float(request.form['angle'])
        operation = request.form['operation']
        if operation == 'sin':
            result = math.sin(math.radians(angle))
        elif operation == 'cos':
            result = math.cos(math.radians(angle))
        elif operation == 'tan':
            result = math.tan(math.radians(angle))
    elif mode == 'derivative':
        # Implement derivative calculations here
        pass
    elif mode == 'integral':
        # Implement integral calculations here
        pass

    # Emit the result to all connected clients
    socketio.emit('result', {'result': result})
    return render_template('index.html', result=result)

if __name__ == '__main__':
    socketio.run(app, debug=True)
