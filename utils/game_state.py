import json
import networkx as nx
import random
from utils.graph import generate_solvable_coloring

class GameState:
    """Class to manage the game state"""
    
    def __init__(self, graph=None, num_colors=4):
        self.graph = graph
        self.available_colors = self._generate_colors(num_colors)
        
        # Initialize all nodes with no color (None)
        self.node_colors = {node: None for node in graph.nodes()} if graph else {}
        
        # Game statistics
        self.moves = 0
        self.hints_used = 0
        self.start_time = None
        self.end_time = None
        
        # Generate a solution (for validation and hints)
        self.solution = generate_solvable_coloring(graph, num_colors) if graph else None
    
    def _generate_colors(self, num_colors):
        """Generate a list of colors"""
        # Predefined colors that work well together and are colorblind-friendly
        color_options = [
            "#4285F4",  # Blue
            "#EA4335",  # Red
            "#FBBC05",  # Yellow
            "#34A853",  # Green
            "#8E44AD",  # Purple
            "#F39C12",  # Orange
            "#1ABC9C",  # Turquoise
            "#E74C3C",  # Crimson
            "#3498DB",  # Light Blue
            "#2ECC71"   # Light Green
        ]
        
        # Return a subset of colors based on num_colors
        return color_options[:min(num_colors, len(color_options))]
    
    def is_complete(self):
        """Check if the game is complete"""
        return all(color is not None for color in self.node_colors.values())
    
    def get_hint(self):
        """
        Generate a hint for the player.
        
        Returns:
            tuple: (node_id, color_index) or None if no hint available
        """
        # Find uncolored nodes
        uncolored_nodes = [node for node, color in self.node_colors.items() if color is None]
        
        if not uncolored_nodes:
            return None
        
        # Choose a random uncolored node
        hint_node = random.choice(uncolored_nodes)
        
        # Get neighboring colors
        neighbor_colors = {self.node_colors[n] for n in self.graph.neighbors(hint_node) 
                          if self.node_colors[n] is not None}
        
        # Find available colors
        available_colors = [i for i in range(len(self.available_colors)) 
                           if i not in neighbor_colors]
        
        if available_colors:
            # Use the solution if available, otherwise pick a random valid color
            if self.solution and hint_node in self.solution:
                hint_color = self.solution[hint_node]
            else:
                hint_color = random.choice(available_colors)
                
            self.hints_used += 1
            return (hint_node, hint_color)
        
        return None
    
    def make_move(self, node, color):
        """
        Make a move in the game
        
        Args:
            node: Node to color
            color: Color index
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Check all neighbors for the same color
        for neighbor in self.graph.neighbors(node):
            if self.node_colors.get(neighbor) == color:
                return False
        
        # Update the node color
        self.node_colors[node] = color
        self.moves += 1
        
        return True
    
    def calculate_score(self, max_score=1000):
        """
        Calculate the player's score based on moves, hints, and time
        
        Args:
            max_score: Maximum possible score
            
        Returns:
            int: Player's score
        """
        if not self.is_complete() or not self.end_time or not self.start_time:
            return 0
        
        # Base score
        score = max_score
        
        # Deduct points for each move beyond the optimal
        optimal_moves = len(self.graph.nodes())
        if self.moves > optimal_moves:
            score -= (self.moves - optimal_moves) * 5
        
        # Deduct points for hints
        score -= self.hints_used * 50
        
        # Deduct points for time (1 point per second after first minute)
        time_taken = (self.end_time - self.start_time).total_seconds()
        if time_taken > 60:
            score -= min(int(time_taken - 60), 300)  # Cap time penalty at 300
        
        # Ensure score doesn't go below 0
        return max(0, score)
    
    def to_json(self):
        """Convert game state to JSON for session storage"""
        # We need to convert the NetworkX graph to a serializable format
        edges = list(self.graph.edges()) if self.graph else []
        nodes = list(self.graph.nodes()) if self.graph else []
        
        state = {
            'graph': {
                'nodes': nodes,
                'edges': edges
            },
            'available_colors': self.available_colors,
            'node_colors': self.node_colors,
            'moves': self.moves,
            'hints_used': self.hints_used,
            'solution': self.solution
        }
        
        return json.dumps(state)
    
    @classmethod
    def from_json(cls, json_data):
        """Create a game state from JSON data"""
        if not json_data:
            return cls()
        
        data = json.loads(json_data)
        
        # Recreate graph from serialized data
        graph = nx.Graph()
        graph.add_nodes_from(data['graph']['nodes'])
        graph.add_edges_from(data['graph']['edges'])
        
        # Create game state
        game_state = cls()
        game_state.graph = graph
        game_state.available_colors = data['available_colors']
        
        # Convert node_colors keys back to integers
        game_state.node_colors = {int(k) if k.isdigit() else k: v for k, v in data['node_colors'].items()}
        game_state.moves = data.get('moves', 0)
        game_state.hints_used = data.get('hints_used', 0)
        game_state.solution = data.get('solution')
        
        # Convert solution keys to integers if they exist
        if game_state.solution:
            game_state.solution = {int(k) if k.isdigit() else k: v for k, v in game_state.solution.items()}
        
        return game_state