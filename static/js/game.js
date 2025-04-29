document.addEventListener('DOMContentLoaded', function () {
    // Game state variables
    let selectedNode = null;
    let selectedColor = null;
    let gameData = null;

    // DOM elements
    const mapContainer = document.getElementById('map-container');
    const colorPalette = document.getElementById('color-palette');
    const messageElement = document.getElementById('message');
    const newGameBtn = document.getElementById('new-game-btn');
    const hintBtn = document.getElementById('hint-btn');
    const difficultySelect = document.getElementById('difficulty');

    // D3 SVG setup
    const svg = d3.select('#map-container')
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%');

    const graphGroup = svg.append('g');

    // Initialize the game
    init();

    function init() {
        // Set up event listeners
        newGameBtn.addEventListener('click', startNewGame);
        hintBtn.addEventListener('click', getHint);

        // Initially disable the hint button until a game starts
        hintBtn.disabled = true;
    }

    function startNewGame() {
        const difficulty = difficultySelect.value;

        // Reset selection state
        selectedNode = null;
        selectedColor = null;

        // Enable hint button
        hintBtn.disabled = false;

        // Send request to create new game
        fetch('/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ difficulty }),
        })
            .then(response => response.json())
            .then(data => {
                gameData = data;
                renderGame(data);
                updateMessage(data.message);
            })
            .catch(error => {
                console.error('Error starting new game:', error);
                updateMessage('Error starting new game. Please try again.');
            });
    }

    function renderGame(data) {
        // Clear previous content
        graphGroup.selectAll('*').remove();
        colorPalette.innerHTML = '';

        // Set up zoom and pan behavior
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                graphGroup.attr('transform', event.transform);
            });

        svg.call(zoom);

        // Reset zoom
        svg.transition().duration(750).call(
            zoom.transform,
            d3.zoomIdentity.translate(mapContainer.clientWidth / 2, mapContainer.clientHeight / 2).scale(0.8)
        );

        // Calculate node radius based on map size
        const nodeRadius = 25;

        // Scale the positions to fit the container
        const positions = data.positions;
        const nodes = data.nodes;

        // Normalize positions to the [0, 1] range
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

        for (const nodeId in positions) {
            const pos = positions[nodeId];
            minX = Math.min(minX, pos.x);
            maxX = Math.max(maxX, pos.x);
            minY = Math.min(minY, pos.y);
            maxY = Math.max(maxY, pos.y);
        }

        const scaledPositions = {};
        for (const nodeId in positions) {
            const pos = positions[nodeId];
            scaledPositions[nodeId] = {
                x: ((pos.x - minX) / (maxX - minX)) * (mapContainer.clientWidth - 2 * nodeRadius) + nodeRadius,
                y: ((pos.y - minY) / (maxY - minY)) * (mapContainer.clientHeight - 2 * nodeRadius) + nodeRadius
            };
        }

        // Draw edges (connections between regions)
        const edges = graphGroup.selectAll('.edge')
            .data(data.edges)
            .enter()
            .append('line')
            .attr('class', 'region-border')
            .attr('x1', d => scaledPositions[d.source].x)
            .attr('y1', d => scaledPositions[d.source].y)
            .attr('x2', d => scaledPositions[d.target].x)
            .attr('y2', d => scaledPositions[d.target].y);

        // Draw nodes (regions)
        const nodeElements = graphGroup.selectAll('.node')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('class', 'region')
            .attr('r', nodeRadius)
            .attr('cx', d => scaledPositions[d.id].x)
            .attr('cy', d => scaledPositions[d.id].y)
            .attr('fill', '#E8E8E8')  // Initial color (uncolored)
            .on('click', function (event, d) {
                selectNode(d.id, this);
            });

        // Add node labels
        graphGroup.selectAll('.node-label')
            .data(nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('x', d => scaledPositions[d.id].x)
            .attr('y', d => scaledPositions[d.id].y + 5)  // Adjust for center alignment
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .text(d => d.id);

        // Create color palette
        data.available_colors.forEach((color, index) => {
            const colorSwatch = document.createElement('div');
            colorSwatch.className = 'color-swatch';
            colorSwatch.style.backgroundColor = color;
            colorSwatch.dataset.colorIndex = index;

            colorSwatch.addEventListener('click', function () {
                selectColor(index, this);
            });

            colorPalette.appendChild(colorSwatch);
        });
    }

    function selectNode(nodeId, element) {
        // Deselect previously selected node
        if (selectedNode !== null) {
            d3.selectAll('.region').classed('selected', false);
        }

        // Select new node
        selectedNode = nodeId;
        d3.select(element).classed('selected', true);

        // If a color is already selected, apply it
        if (selectedColor !== null) {
            applyColorToNode();
        }
    }

    function selectColor(colorIndex, element) {
        // Deselect previously selected color
        if (selectedColor !== null) {
            document.querySelectorAll('.color-swatch').forEach(swatch => {
                swatch.classList.remove('selected');
            });
        }

        // Select new color
        selectedColor = colorIndex;
        element.classList.add('selected');

        // If a node is already selected, apply the color
        if (selectedNode !== null) {
            applyColorToNode();
        }
    }

    function applyColorToNode() {
        if (selectedNode === null || selectedColor === null) return;

        fetch('/color_node', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                node_id: selectedNode,
                color_index: selectedColor
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    updateNodeColors(data.node_colors);
                    updateMessage(data.message);

                    // Check if game is complete
                    if (data.game_complete) {
                        celebrateVictory();
                    }
                } else {
                    updateMessage(data.message);
                    // Shake effect for invalid move
                    d3.select('.selected')
                        .transition()
                        .duration(50)
                        .attr('transform', 'translate(3, 0)')
                        .transition()
                        .duration(50)
                        .attr('transform', 'translate(-3, 0)')
                        .transition()
                        .duration(50)
                        .attr('transform', 'translate(3, 0)')
                        .transition()
                        .duration(50)
                        .attr('transform', 'translate(0, 0)');
                }

                // Deselect the node after application (success or failure)
                d3.selectAll('.region').classed('selected', false);
                selectedNode = null;
            })
            .catch(error => {
                console.error('Error applying color:', error);
                updateMessage('Error applying color. Please try again.');
            });
    }

    function updateNodeColors(nodeColors) {
        for (const nodeId in nodeColors) {
            const colorIndex = nodeColors[nodeId];
            if (colorIndex !== null) {
                const color = gameData.available_colors[colorIndex];
                d3.selectAll('.region')
                    .filter((d) => d.id === nodeId)
                    .attr('fill', color);
            }
        }
    }

    function getHint() {
        fetch('/hint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
            .then(response => response.json())
            .then(data => {
                updateMessage(data.message);

                // Highlight the hint node
                if (data.hint_node) {
                    // Flash the suggested node
                    d3.selectAll('.region')
                        .filter((d) => d.id === data.hint_node)
                        .transition()
                        .duration(300)
                        .attr('stroke', '#FF5722')
                        .attr('stroke-width', 4)
                        .transition()
                        .duration(300)
                        .attr('stroke', '#333')
                        .attr('stroke-width', 1.5);
                }
            })
            .catch(error => {
                console.error('Error getting hint:', error);
                updateMessage('Error getting hint. Please try again.');
            });
    }

    function updateMessage(message) {
        messageElement.textContent = message;

        // Apply a subtle animation to draw attention to the message
        messageElement.style.transform = 'scale(1.05)';
        setTimeout(() => {
            messageElement.style.transform = 'scale(1)';
        }, 200);
    }

    function celebrateVictory() {
        // Visual celebration for completing the game
        svg.append('g')
            .attr('class', 'confetti')
            .selectAll('circle')
            .data(d3.range(100))
            .enter()
            .append('circle')
            .attr('r', () => Math.random() * 8 + 2)
            .attr('cx', () => Math.random() * mapContainer.clientWidth)
            .attr('cy', () => -10)
            .attr('fill', () => {
                const colors = gameData.available_colors;
                return colors[Math.floor(Math.random() * colors.length)];
            })
            .transition()
            .duration(() => Math.random() * 2000 + 1000)
            .ease(d3.easeLinear)
            .attr('cy', mapContainer.clientHeight + 10)
            .remove();

        // Disable hint button after victory
        hintBtn.disabled = true;
    }

    // Handle window resize
    window.addEventListener('resize', function () {
        if (gameData) {
            renderGame(gameData);
        }
    });
});