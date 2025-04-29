from flask import Flask, render_template, request, jsonify, session
import json
import os
import random
import datetime
from utils.graph import create_planar_graph, is_valid_coloring
from utils.game_state import GameState

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Game difficulty levels
DIFFICULTY_LEVELS = {
    'easy': {'nodes': 10, 'colors': 4},
    'medium': {'nodes': 15, 'colors': 4},
    'hard': {'nodes': 20, 'colors': 4}
}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_game', methods=['POST'])
def new_game():
    difficulty = request.json.get('difficulty', 'medium')
    map_type = request.json.get('map_type', 'random')
    
    # Get parameters based on difficulty
    params = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS['medium'])
    
    # Create a new graph
    graph, positions = create_planar_graph(params['nodes'], map_type)
    
    # Create game state
    game_state = GameState(graph, params['colors'])
    
    # Set start time
    game_state.start_time = datetime.datetime.now()
    
    # Convert node positions to a format suitable for frontend
    node_positions = {str(node): {'x': pos[0], 'y': pos[1]} for node, pos in positions.items()}
    
    # Create a list of edges for the frontend
    edges = [{'source': str(u), 'target': str(v)} for u, v in graph.edges()]
    
    # Save game state in session
    session['game_state'] = game_state.to_json()
    session['difficulty'] = difficulty
    session['map_type'] = map_type
    
    return jsonify({
        'nodes': [{'id': str(node)} for node in graph.nodes()],
        'edges': edges,
        'positions': node_positions,
        'available_colors': game_state.available_colors,
        'message': f'New {difficulty} game started. Color the regions!',
        'game_complete': False
    })

@app.route('/color_node', methods=['POST'])
def color_node():
    node_id = request.json.get('node_id')
    color_index = request.json.get('color_index')
    
    # Load game state from session
    game_state = GameState.from_json(session.get('game_state', '{}'))
    
    if not game_state.graph:
        return jsonify({'error': 'No active game'}), 400
    
    # Convert node_id to integer (it's sent as string from frontend)
    node_id = int(node_id)
    
    # Check if the coloring is valid and make the move
    if game_state.make_move(node_id, color_index):
        # Check if the game is complete
        game_complete = game_state.is_complete()
        
        # Record end time if game is complete
        if game_complete:
            game_state.end_time = datetime.datetime.now()
            
            # Calculate time safely - ensure both start_time and end_time exist
            time_seconds = 0
            if game_state.start_time is not None and game_state.end_time is not None:
                time_seconds = int((game_state.end_time - game_state.start_time).total_seconds())
            
            # Record game statistics
            record_game_stats(
                difficulty=session.get('difficulty', 'medium'),
                moves=game_state.moves,
                hints=game_state.hints_used,
                time_seconds=time_seconds,
                score=game_state.calculate_score()
            )
        
        # Save updated game state
        session['game_state'] = game_state.to_json()
        
        message = "Valid move!"
        if game_complete:
            message = f"Congratulations! You've completed the map coloring in {game_state.moves} moves!"
        
        return jsonify({
            'valid': True,
            'node_colors': {str(k): v for k, v in game_state.node_colors.items()},
            'message': message,
            'game_complete': game_complete,
            'moves': game_state.moves,
            'score': game_state.calculate_score() if game_complete else None
        })
    else:
        return jsonify({
            'valid': False,
            'message': "Invalid move! Adjacent regions can't have the same color."
        })

@app.route('/hint', methods=['POST'])
def hint():
    # Load game state from session
    game_state = GameState.from_json(session.get('game_state', '{}'))
    
    if not game_state.graph:
        return jsonify({'error': 'No active game'}), 400
    
    # Get a hint from the game state
    hint_data = game_state.get_hint()
    
    if hint_data:
        hint_node, hint_color = hint_data
        hint_message = f"Try coloring node {hint_node} with {game_state.available_colors[hint_color]}."
        
        # Save the updated hint count
        session['game_state'] = game_state.to_json()
        
        return jsonify({
            'hint_node': str(hint_node),
            'hint_color': hint_color,
            'message': hint_message
        })
    else:
        return jsonify({
            'message': 'No hint available at this time.'
        })

@app.route('/save_settings', methods=['POST'])
def save_settings():
    # Get settings from request
    settings = request.json
    
    # Save settings in session
    session['settings'] = json.dumps(settings)
    
    return jsonify({'success': True})

@app.route('/get_settings', methods=['GET'])
def get_settings():
    # Get settings from session
    settings = json.loads(session.get('settings', '{}'))
    
    # Return default settings if not set
    if not settings:
        settings = {
            'colorblind_mode': False,
            'show_node_labels': True,
            'animation_speed': 'normal'
        }
    
    return jsonify(settings)

def record_game_stats(difficulty, moves, hints, time_seconds, score):
    """
    Record game statistics in a cookie for the client to store
    
    This is just a helper function to format the data - the actual
    storage will happen in the client-side JavaScript using localStorage
    """
    game_data = {
        'difficulty': difficulty,
        'moves': moves,
        'hints': hints,
        'time': time_seconds,
        'score': score,
        'date': datetime.datetime.now().isoformat()
    }
    
    return jsonify(game_data)

@app.route('/get_game_stats', methods=['GET'])
def get_game_stats():
    """Return the stats of the current game for saving to localStorage"""
    # Load game state from session
    game_state = GameState.from_json(session.get('game_state', '{}'))
    
    if not game_state.graph:
        return jsonify({'error': 'No active game'}), 400
    
    # Calculate time safely
    time_seconds = 0
    if hasattr(game_state, 'start_time') and hasattr(game_state, 'end_time') and \
       game_state.start_time is not None and game_state.end_time is not None:
        time_seconds = int((game_state.end_time - game_state.start_time).total_seconds())
    else:
        # If we don't have valid timestamps, set the end time to now
        if not hasattr(game_state, 'end_time') or game_state.end_time is None:
            game_state.end_time = datetime.datetime.now()
        
        # If start time is missing, assume it just started
        if not hasattr(game_state, 'start_time') or game_state.start_time is None:
            game_state.start_time = game_state.end_time
            time_seconds = 0
    
    # Compile game stats
    stats = {
        'difficulty': session.get('difficulty', 'medium'),
        'moves': game_state.moves,
        'hints': game_state.hints_used,
        'time': time_seconds,
        'score': game_state.calculate_score(),
        'date': datetime.datetime.now().isoformat()
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)