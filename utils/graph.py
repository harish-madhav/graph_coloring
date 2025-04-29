import networkx as nx
import random
import math
import numpy as np

def create_planar_graph(num_nodes, map_type="random"):
    """
    Create a planar graph representing a map with regions.
    
    Args:
        num_nodes: Number of nodes (regions) to create
        map_type: Type of map to generate ("random", "grid", "voronoi")
        
    Returns:
        graph: NetworkX graph
        positions: Dictionary of node positions
    """
    if map_type == "grid":
        return create_grid_graph(num_nodes)
    elif map_type == "voronoi":
        return create_voronoi_graph(num_nodes)
    else:  # Default to random planar graph
        return create_random_planar_graph(num_nodes)

def create_random_planar_graph(num_nodes):
    """Create a random planar graph"""
    # Create random points for a Delaunay triangulation
    points = []
    for _ in range(num_nodes):
        # Generate points within a unit square with some margin
        x = 0.1 + 0.8 * random.random()  # Keep away from edges
        y = 0.1 + 0.8 * random.random()
        points.append((x, y))
    
    # Create a graph
    graph = nx.Graph()
    
    # Add nodes
    for i in range(num_nodes):
        graph.add_node(i)
    
    # Create positions dictionary
    positions = {i: (x, y) for i, (x, y) in enumerate(points)}
    
    # Add edges based on proximity
    for i in range(num_nodes):
        # Find the 3-5 nearest neighbors for each node
        neighbors = []
        for j in range(num_nodes):
            if i != j:
                x1, y1 = points[i]
                x2, y2 = points[j]
                dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                neighbors.append((j, dist))
        
        # Sort by distance and connect to 2-4 nearest neighbors
        neighbors.sort(key=lambda x: x[1])
        connections = random.randint(2, min(4, len(neighbors)))
        for j in range(connections):
            graph.add_edge(i, neighbors[j][0])
    
    # Ensure the graph is connected
    if not nx.is_connected(graph):
        components = list(nx.connected_components(graph))
        for i in range(len(components) - 1):
            node1 = random.choice(list(components[i]))
            node2 = random.choice(list(components[i+1]))
            graph.add_edge(node1, node2)
    
    return graph, positions

def create_grid_graph(num_nodes):
    """Create a grid-like graph"""
    # Determine dimensions for a roughly square grid
    side = math.ceil(math.sqrt(num_nodes))
    
    # Create a grid graph
    grid = nx.grid_2d_graph(side, side)
    
    # Convert to a simple graph with integer nodes
    graph = nx.Graph()
    node_mapping = {}
    
    for i, node in enumerate(list(grid.nodes())[:num_nodes]):
        node_mapping[node] = i
        graph.add_node(i)
    
    # Add edges
    for u, v in grid.edges():
        if u in node_mapping and v in node_mapping:
            graph.add_edge(node_mapping[u], node_mapping[v])
    
    # Position nodes in a grid layout
    positions = {}
    for (x, y), i in node_mapping.items():
        positions[i] = (x / (side - 1), y / (side - 1))
    
    return graph, positions

def create_voronoi_graph(num_nodes):
    """Create a Voronoi-based graph (more map-like)"""
    # Generate random points
    points = []
    for _ in range(num_nodes):
        x = 0.1 + 0.8 * random.random()
        y = 0.1 + 0.8 * random.random()
        points.append((x, y))
    
    # Create graph
    graph = nx.Graph()
    
    # Add nodes
    for i in range(num_nodes):
        graph.add_node(i)
    
    # Create positions dictionary
    positions = {i: (x, y) for i, (x, y) in enumerate(points)}
    
    # Compute a Delaunay triangulation to approximate Voronoi neighbors
    # We'll use a basic approach to compute neighbors
    for i in range(num_nodes):
        x1, y1 = points[i]
        # Connect to nodes that are natural neighbors in a Voronoi sense
        for j in range(i+1, num_nodes):
            x2, y2 = points[j]
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # Check if there's any point closer to the midpoint than these two points
            midpoint = ((x1+x2)/2, (y1+y2)/2)
            is_neighbor = True
            
            for k in range(num_nodes):
                if k != i and k != j:
                    x3, y3 = points[k]
                    dist_to_mid = math.sqrt((midpoint[0]-x3)**2 + (midpoint[1]-y3)**2)
                    dist_to_i = math.sqrt((midpoint[0]-x1)**2 + (midpoint[1]-y1)**2)
                    if dist_to_mid < dist_to_i:
                        is_neighbor = False
                        break
            
            # If no point is closer to the midpoint, add an edge
            if is_neighbor and dist < 0.3:  # Limit the connection distance
                graph.add_edge(i, j)
    
    # Ensure the graph is connected
    if not nx.is_connected(graph):
        components = list(nx.connected_components(graph))
        for i in range(len(components) - 1):
            node1 = random.choice(list(components[i]))
            node2 = random.choice(list(components[i+1]))
            graph.add_edge(node1, node2)
    
    return graph, positions

def is_valid_coloring(graph, node_colors, node, color):
    """
    Check if coloring a node with a specific color is valid.
    
    Args:
        graph: NetworkX graph
        node_colors: Dictionary mapping nodes to colors
        node: Node to color
        color: Color index
        
    Returns:
        bool: True if coloring is valid, False otherwise
    """
    # Check if neighbors have the same color
    for neighbor in graph.neighbors(node):
        if node_colors.get(neighbor) == color:
            return False
    
    return True

def suggest_color(graph, node_colors, node):
    """
    Suggest a valid color for a node.
    
    Args:
        graph: NetworkX graph
        node_colors: Dictionary mapping nodes to colors
        node: Node to suggest a color for
        
    Returns:
        int: Suggested color index or None if no color is valid
    """
    # Get colors used by neighbors
    neighbor_colors = set()
    for neighbor in graph.neighbors(node):
        if node_colors.get(neighbor) is not None:
            neighbor_colors.add(node_colors[neighbor])
    
    # Determine available colors (assuming 4 colors are available)
    available_colors = [i for i in range(4) if i not in neighbor_colors]
    
    if available_colors:
        return random.choice(available_colors)
    else:
        return None

def generate_solvable_coloring(graph, num_colors=4):
    """
    Generate a valid coloring solution for the graph.
    
    Args:
        graph: NetworkX graph
        num_colors: Number of colors to use
        
    Returns:
        dict: A valid coloring or None if not possible
    """
    # Use the greedy coloring algorithm as a base
    coloring = {}
    nodes = list(graph.nodes())
    random.shuffle(nodes)  # Randomize order for different solutions
    
    for node in nodes:
        # Find colors used by neighbors
        used_colors = {coloring[neighbor] for neighbor in graph.neighbors(node) 
                      if neighbor in coloring}
        
        # Find the first available color
        for color in range(num_colors):
            if color not in used_colors:
                coloring[node] = color
                break
        else:
            # If we couldn't find a color, backtrack or fail
            return None
    
    return coloring