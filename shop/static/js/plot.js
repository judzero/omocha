// static/js/plot.js
document.addEventListener('DOMContentLoaded', function () {
    // Sample data
    var data = [
        {
            x: [1, 2, 3, 4, 5],
            y: [10, 11, 12, 13, 14],
            type: 'bar',
            name: 'Board Games',  // Name of the trace
            xaxis: 'x'        // Assign the trace to the first x-axis
        },
        {
            x: [10, 20, 30, 40, 50],
            y: [5, 4, 3, 2, 1],
            type: 'bar',
            name: 'Puzzles',  // Name of the trace
            xaxis: 'x2'       // Assign the trace to the second x-axis
        }
    ];

    // Layout options with two x-axes
    var layout = {
        title: 'Plotly Chart with Two X-Axes',
        showlegend: true,
        xaxis2: {
            overlaying: 'x',  // Overlay the second x-axis on top of the first one
            side: 'top'       // Position the second x-axis at the top
        },
    };

    // Create Plotly chart
    Plotly.newPlot('chart-container', data, layout);
});
