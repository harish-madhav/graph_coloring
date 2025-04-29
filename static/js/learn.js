document.addEventListener('DOMContentLoaded', function () {
    // Navigation between sections
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.content-section');

    // Back to game button
    const backToGameBtn = document.getElementById('back-to-game-btn');

    // Set up navigation
    navButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons and sections
            navButtons.forEach(btn => btn.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Show corresponding section
            const sectionId = this.dataset.section;
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // Back to game button
    backToGameBtn.addEventListener('click', function () {
        window.location.href = '/';
    });

    // Create D3.js visualizations for examples
    createBasicGraphExample();
    createMapColoringExample();
    createSchedulingExample();
});

function createBasicGraphExample() {
    const container = document.getElementById('basic-graph-example');
    if (!container) return;

    // Set up dimensions
    const width = container.clientWidth;
    const height = 250;

    // Create SVG
    const svg = d3.select('#basic-graph-example')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Define a simple graph
    const nodes = [
        { id: 0, x: width * 0.2, y: height * 0.3, color: "#4285F4" },  // Blue
        { id: 1, x: width * 0.4, y: height * 0.7, color: "#EA4335" },  // Red
        { id: 2, x: width * 0.6, y: height * 0.3, color: "#FBBC05" },  // Yellow
        { id: 3, x: width * 0.8, y: height * 0.7, color: "#4285F4" },  // Blue
        { id: 4, x: width * 0.5, y: height * 0.5, color: "#34A853" }   // Green
    ];

    const links = [
        { source: 0, target: 1 },
        { source: 0, target: 4 },
        { source: 1, target: 2 },
        { source: 1, target: 4 },
        { source: 2, target: 3 },
        { source: 2, target: 4 },
        { source: 3, target: 4 }
    ];

    // Draw edges
    svg.selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('x1', d => nodes[d.source].x)
        .attr('y1', d => nodes[d.source].y)
        .attr('x2', d => nodes[d.target].x)
        .attr('y2', d => nodes[d.target].y)
        .attr('stroke', '#333')
        .attr('stroke-width', 2);

    // Draw nodes
    svg.selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 20)
        .attr('fill', d => d.color)
        .attr('stroke', '#333')
        .attr('stroke-width', 2);

    // Add node labels
    svg.selectAll('text')
        .data(nodes)
        .enter()
        .append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y + 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .attr('fill', 'white')
        .text(d => d.id);

    // Add animation to demonstrate the concept
    function highlightAdjacent() {
        const randomNodeIndex = Math.floor(Math.random() * nodes.length);
        const adjacentNodes = links
            .filter(link => link.source === randomNodeIndex || link.target === randomNodeIndex)
            .map(link => link.source === randomNodeIndex ? link.target : link.source);

        // Highlight the selected node
        svg.selectAll('circle')
            .transition()
            .duration(500)
            .attr('r', d => d.id === randomNodeIndex ? 25 : 20)
            .attr('stroke-width', d => d.id === randomNodeIndex ? 3 : 2);

        // Highlight adjacent edges
        svg.selectAll('line')
            .transition()
            .duration(500)
            .attr('stroke-width', d => {
                if (d.source === randomNodeIndex || d.target === randomNodeIndex) {
                    return 4;
                }
                return 2;
            })
            .attr('stroke', d => {
                if (d.source === randomNodeIndex || d.target === randomNodeIndex) {
                    return '#000';
                }
                return '#333';
            });

        // Add a delay and reset
        setTimeout(() => {
            svg.selectAll('circle')
                .transition()
                .duration(500)
                .attr('r', 20)
                .attr('stroke-width', 2);

            svg.selectAll('line')
                .transition()
                .duration(500)
                .attr('stroke-width', 2)
                .attr('stroke', '#333');
        }, 1500);
    }

    // Run the animation every 3 seconds
    setInterval(highlightAdjacent, 3000);
}

function createMapColoringExample() {
    const container = document.getElementById('map-coloring-example');
    if (!container) return;

    // Set up dimensions
    const width = container.clientWidth;
    const height = 300;

    // Create SVG
    const svg = d3.select('#map-coloring-example')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Define a simple map with regions
    const regions = [
        { id: 'A', path: `M10,10 L${width / 3},10 L${width / 3},${height / 2} L10,${height / 2} Z`, color: "#4285F4" },
        { id: 'B', path: `M${width / 3},10 L${2 * width / 3},10 L${2 * width / 3},${height / 2} L${width / 3},${height / 2} Z`, color: "#EA4335" },
        { id: 'C', path: `M${2 * width / 3},10 L${width - 10},10 L${width - 10},${height / 2} L${2 * width / 3},${height / 2} Z`, color: "#4285F4" },
        { id: 'D', path: `M10,${height / 2} L${width / 3},${height / 2} L${width / 3},${height - 10} L10,${height - 10} Z`, color: "#34A853" },
        { id: 'E', path: `M${width / 3},${height / 2} L${2 * width / 3},${height / 2} L${2 * width / 3},${height - 10} L${width / 3},${height - 10} Z`, color: "#FBBC05" },
        { id: 'F', path: `M${2 * width / 3},${height / 2} L${width - 10},${height / 2} L${width - 10},${height - 10} L${2 * width / 3},${height - 10} Z`, color: "#34A853" }
    ];

    // Draw regions
    svg.selectAll('path')
        .data(regions)
        .enter()
        .append('path')
        .attr('d', d => d.path)
        .attr('fill', d => d.color)
        .attr('stroke', '#333')
        .attr('stroke-width', 2);

    // Add region labels
    svg.selectAll('text')
        .data(regions)
        .enter()
        .append('text')
        .attr('x', d => {
            const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathElement.setAttribute('d', d.path);
            const bbox = pathElement.getBBox();
            return bbox.x + bbox.width / 2;
        })
        .attr('y', d => {
            const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathElement.setAttribute('d', d.path);
            const bbox = pathElement.getBBox();
            return bbox.y + bbox.height / 2 + 5;
        })
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .attr('font-weight', 'bold')
        .attr('fill', '#333')
        .text(d => d.id);

    // Add animation to demonstrate four colors are sufficient
    let colorIndex = 0;
    const colorSchemes = [
        ["#4285F4", "#EA4335", "#4285F4", "#34A853", "#FBBC05", "#34A853"], // Original
        ["#34A853", "#FBBC05", "#34A853", "#4285F4", "#EA4335", "#4285F4"], // Scheme 2
        ["#FBBC05", "#4285F4", "#FBBC05", "#EA4335", "#34A853", "#EA4335"], // Scheme 3
        ["#EA4335", "#34A853", "#EA4335", "#FBBC05", "#4285F4", "#FBBC05"]  // Scheme