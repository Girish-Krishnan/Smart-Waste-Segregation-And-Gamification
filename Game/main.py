import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from game_logic import GameState

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'green_future_secret'
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow local connections

# Initialize game state
game_state = GameState()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logging.debug('Client connected')

@socketio.on('player_move')
def handle_move(data):
    game_state.update_player_position(data)
    socketio.emit('game_state_update', game_state.get_state())

@socketio.on('player_shoot')
def handle_shoot(data):
    game_state.process_shot(data)
    socketio.emit('game_state_update', game_state.get_state())

@socketio.on('joystick_input')
def handle_joystick_input(data):
    """Handle input from Raspberry Pi joysticks"""
    logging.debug(f'Joystick input received: {data}')
    # Broadcast the joystick input to all connected clients
    socketio.emit('joystick_data', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)