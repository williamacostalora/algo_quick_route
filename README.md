# QuickRoute: Transit Pathfinding Algorithm Comparison

A comprehensive Python implementation and comparative analysis of pathfinding algorithms (Dijkstra's, Floyd-Warshall, A*, and Weighted A*) applied to the Twin Cities Metro Transit system.

## Project Overview

This project converts a previous Java implementation to Python and extends it with multiple pathfinding algorithms for academic comparison. It includes:

- **Four pathfinding algorithms**: Dijkstra's, Floyd-Warshall, A*, and Weighted A*
- **Real-world data**: Integration with Metro Transit NexTrip API
- **Performance benchmarking**: Comprehensive comparison framework
- **Academic paper**: LaTeX document comparing algorithm performance
- **Interactive application**: User-friendly route finding tool

## Features

### Algorithms Implemented

1. **Dijkstra's Algorithm**
   - Guaranteed optimal solution
   - Single-source shortest path
   - Time complexity: O((V + E) log V)

2. **Floyd-Warshall Algorithm**
   - All-pairs shortest paths
   - Dynamic programming approach
   - Time complexity: O(V³)

3. **A* Search**
   - Informed search with heuristic
   - Optimal with admissible heuristic
   - Uses geographic distance heuristic

4. **Weighted A***
   - Tunable trade-off between speed and optimality
   - Configurable weight parameter
   - Faster but potentially suboptimal

### Performance Metrics

The comparison framework measures:
- Execution time (seconds)
- Nodes explored
- Path length (number of stops)
- Total transit time (minutes)
- Solution optimality

## Project Structure

```
.
├── api_caller.py              # Metro Transit API interface
├── stop.py                    # Stop (vertex) class
├── edge.py                    # Edge class
├── graph.py                   # Graph class with all algorithms
├── algorithm_comparison.py    # Benchmarking framework
├── quickroute.py             # Main interactive application
├── graph_serializer.py       # Pre-build and save graphs
├── algorithm_comparison_paper.tex  # LaTeX research paper
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- LaTeX distribution (for compiling the paper)

### Setup

1. Clone or download the repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Build the transit graph (this may take several minutes):
```bash
python graph_serializer.py
```
   Choose option 1 for the full multi-route graph, or option 2 for a small test graph.

## Usage

### Interactive Route Finding

Run the main QuickRoute application:

```bash
python quickroute.py
```

Follow the prompts to:
1. Select a departure stop
2. Select a destination stop
3. Choose an algorithm
4. View the optimal route

### Algorithm Comparison

Run the comparison framework:

```bash
python algorithm_comparison.py
```

This will:
- Compare all algorithms on test routes
- Generate performance metrics
- Create visualization plots
- Export results to text and LaTeX formats

### Compiling the Research Paper

Compile the LaTeX paper:

```bash
pdflatex algorithm_comparison_paper.tex
bibtex algorithm_comparison_paper
pdflatex algorithm_comparison_paper.tex
pdflatex algorithm_comparison_paper.tex
```

Or use your preferred LaTeX editor (TeXShop, Overleaf, etc.)

## Available Transit Routes

The system includes the following Metro Transit routes:

- **Blue Line (901)**: MSP Airport to Downtown Minneapolis
- **Green Line (902)**: Downtown Minneapolis to Downtown Saint Paul
- **A Line (921)**: Rosedale to 46th Street Station
- **Route 63**: Grand Ave and Snelling (Macalester) to Downtown Saint Paul

## Key Stops

Pre-configured stops include:
- Terminal 1 Station (MSP Airport)
- Mall of America Station
- Downtown Saint Paul (5th St & Jackson St)
- Downtown Minneapolis (Warehouse District/Hennepin Ave)
- Macalester College (Grand Ave & Snelling Ave)
- Snelling & Grand Station
- Minnehaha Falls (46th St Station)

## API Integration

This project uses the Metro Transit NexTrip API:
- Base URL: `https://svc.metrotransit.org/`
- Documentation: https://svc.metrotransit.org/swagger/index.html
- No API key required (public access)

## Performance Results (Example)

| Algorithm | Exec Time (s) | Nodes Explored | Path Length | Transit Time (min) |
|-----------|---------------|----------------|-------------|-------------------|
| Dijkstra | 0.0234 | 156 | 12 | 28.5 |
| Floyd-Warshall | 0.8765 | 8000000 | 12 | 28.5 |
| A* | 0.0089 | 62 | 12 | 28.5 |
| Weighted A* (1.5) | 0.0045 | 41 | 12 | 31.9 |
| Weighted A* (2.0) | 0.0031 | 28 | 13 | 33.6 |

*Note: Results vary based on route and network size*

## Conversion from Java

This project is a Python conversion and extension of a previous Java implementation. Key improvements include:

1. **More Pythonic**: Uses Python idioms and data structures
2. **Additional Algorithms**: Added Floyd-Warshall and Weighted A*
3. **Benchmarking Framework**: Comprehensive comparison tools
4. **Visualization**: Matplotlib-based performance plots
5. **Research Paper**: Academic LaTeX document

## Research Paper

The included LaTeX paper provides:
- Theoretical background on each algorithm
- Complexity analysis
- Empirical performance comparison
- Discussion of trade-offs
- Practical recommendations
- Future research directions

### Paper Sections

1. Introduction and motivation
2. Background and related work
3. Methodology and implementation
4. Experimental results
5. Discussion
6. Conclusion and future work
7. Appendices with pseudocode

## Customization

### Adding New Routes

Edit `graph_serializer.py` to include additional routes:

```python
routes = [
    (route_id, direction_id, "Route Description"),
    # Add more routes here
]
```

### Modifying the Heuristic

Edit the heuristic function in `graph.py`:

```python
def heuristic(stop: Stop) -> float:
    # Implement custom heuristic
    return estimated_cost
```

### Adjusting Weighted A* Weight

When calling `weighted_a_star()`, specify the weight:

```python
path, time, metrics = graph.weighted_a_star(start_id, dest_id, weight=1.5)
```

## Troubleshooting

### API Errors

If you encounter API errors:
- Check your internet connection
- Verify the Metro Transit API is operational
- Ensure stop IDs and route IDs are valid

### Memory Issues

For large networks, Floyd-Warshall may consume significant memory. Consider:
- Using the test graph for development
- Increasing available system memory
- Limiting the number of routes included

### Performance

If algorithms run slowly:
- Ensure the graph is pre-serialized (run `graph_serializer.py`)
- Use A* or Weighted A* for faster results
- Consider reducing the network size

## Dependencies

- `requests`: API calls
- `matplotlib`: Visualization
- `numpy`: Numerical operations
- `pickle`: Graph serialization

See `requirements.txt` for specific versions.

## Contributing

This is an academic project, but suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

## Future Enhancements

Potential areas for expansion:

1. **Time-dependent routing**: Incorporate schedules
2. **Multi-objective optimization**: Minimize time, cost, transfers
3. **Real-time updates**: Handle delays and service disruptions
4. **Mobile application**: Responsive web or mobile app
5. **Machine learning**: Learned heuristics for A*
6. **Contraction hierarchies**: Advanced preprocessing
7. **Bidirectional search**: Meet-in-the-middle approach

## Academic Context

This project was developed as part of computer science coursework at Macalester College, exploring:
- Graph algorithms and data structures
- Algorithm analysis and optimization
- Software engineering best practices
- Technical writing and research methodology

## License

This project is for educational purposes. Metro Transit data is accessed via their public API.

## Contact

**Author**: William Andres Sanchez  
**Email**: wsanche2@macalester.edu  
**Institution**: Macalester College  
**Department**: Computer Science

## Acknowledgments

- Metro Transit for providing public API access
- Macalester College Computer Science Department
- Original Java project contributors
- Academic advisors and reviewers

## References

1. Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs"
2. Floyd, R. W. (1962). "Algorithm 97: Shortest path"
3. Hart, P. E., et al. (1968). "A formal basis for the heuristic determination of minimum cost paths"
4. Pohl, I. (1970). "Heuristic search viewed as path finding in a graph"

For complete references, see the research paper bibliography.

---

**Last Updated**: December 2024  
**Version**: 1.0
