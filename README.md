# Transit Routing Algorithms

A comparison of 6 pathfinding algorithms applied to the Twin Cities Metro Transit system.

## What It Does

Finds the fastest route between two bus/train stops using:
- **Dijkstra's Algorithm** - Classic, guaranteed optimal
- **A* Search** - Smart and fast, uses geographic hints
- **Floyd-Warshall** - Computes all routes at once
- **Weighted A*** - Fastest but slightly suboptimal
- **BFS** - Searches through all nodes, focusing on breadth
- **DFS** - Searches through all nodes, focusing on depth


## Quick Start

### Initial Setup (First Time Only)

Run these commands **in order** to set up the project correctly:

```bash
# Step 1: Build the transit graph from Metro Transit API
python3 graph_serializer.py

# Step 2: Fix the Stop class comparison issue
# (Already fixed in stop.py - no action needed)

# Step 3: Apply transfer penalty fix (CRITICAL - prevents shortcuts)
python3 fix_transfer_penalty.py

# Step 4: Verify the graph is working correctly
python3 test_routes.py
```

**Expected Result:** Routes should show direct paths (e.g., 20 stops for Mall of America → Target Field) without unnecessary transfers.

### Regular Usage (After Setup)

Once setup is complete, use these commands:

```bash
# Find a route interactively
python3 quickroute.py

# Run performance tests and generate graphs
python3 test_algorithm_performance.py
```

## Daily Usage

1. **Find a route:**
```bash
python3 quickroute.py
```

2. **Run performance comparison:**
```bash
python3 test_algorithm_performance.py
```

This generates:
- `algorithm_performance_comparison.png` - Performance graphs
- `performance_table.tex` - LaTeX table for papers

## Files

### Core Algorithm Files
| File | Purpose |
|------|---------|
| `dijkstra.py` | Dijkstra's algorithm implementation |
| `a_star.py` | A* search implementation |
| `weighted_a_star.py` | Weighted A* implementation |
| `floyd_warshall.py` | Floyd-Warshall implementation |
| `BFS.py` | Dijkstra's algorithm implementation |
| `DFS.py` | Dijkstra's algorithm implementation |

### Data & Graph Files
| File | Purpose |
|------|---------|
| `api_caller.py` | Fetches Metro Transit data |
| `graph_serializer.py` | Builds the transit network |
| `stop.py` | Transit stop class (with comparison fixes) |
| `edge.py` | Connection between stops |

### Application Files
| File | Purpose |
|------|---------|
| `quickroute.py` | Interactive route finder |
| `test_algorithm_performance.py` | Performance comparison tool |

### Fix & Diagnostic Tools
| File | Purpose |
|------|---------|
| `fix_transfer_penalty.py` | **REQUIRED** - Fixes transfer shortcuts (run after building graph) |
| `diagnose_graph.py` | Analyzes graph structure |
| `debug_route.py` | Traces exact paths for debugging |
| `test_routes.py` | Tests predefined interesting routes |

## Results

- **A* is 2-3x faster** than Dijkstra
- **A* explores 60% fewer stops** than Dijkstra
- Both find the **optimal route**
- **Weighted A* is fastest** (3-5x speedup) but routes are slightly longer

## Example Usage

```python
from dijkstra import dijkstra_algorithm
from a_star import a_star_algorithm

# Load the graph
graph = load_graph('transit_graph.pkl')

# Find route from Mall of America to Target Field
start = graph.stops[30]  # Mall of America
end = graph.stops[44]    # Target Field

# Compare algorithms
dijkstra_path = dijkstra_algorithm(graph, start, end)
astar_path = a_star_algorithm(graph, start, end)
```

## Network Data

- **55 transit stops**
- **2,248 connections**
- **4 routes:** Blue Line, Green Line, A Line, Route 63
- Real GPS coordinates and travel times

## Important Fixes & Troubleshooting

### 1. Stop Class Comparison Error
**Problem:** `'<' not supported between instances of 'Stop' and 'Stop'`

**Solution:** Added comparison methods to `stop.py`:
```python
def __lt__(self, other):
    return self.stop_id < other.stop_id
```

### 2. Transfer Edge Shortcuts
**Problem:** Routes showing only 3-8 stops instead of full 20-stop direct routes.

**Root Cause:** Transfer edges with 0 minutes created unrealistic shortcuts between stops on the same route.

**Solution:** Applied `fix_transfer_penalty.py` to:
- Set 15-minute penalty for ALL transfer edges
- Ensures direct routes are preferred over transfers
- Reflects real-world waiting + walking time

### 3. API Direction IDs
**Problem:** Code tried to fetch directions 0-3, but API returns 403 errors.

**Solution:** Metro Transit API only provides 2 directions per route (0 and 1):
- Direction 0: One direction (e.g., Northbound, Eastbound)
- Direction 1: Opposite direction (e.g., Southbound, Westbound)

### 4. File Paths
**Problem:** Code referenced `/mnt/user-data/outputs/` which doesn't exist locally.

**Solution:** Updated `test_algorithm_performance.py` to save files in current directory (`./`).

## Testing Your Graph

After building your graph, verify it's working correctly:

```bash
# Diagnose graph structure
python3 diagnose_graph.py

# Debug specific routes
python3 debug_route.py

# Test predefined routes
python3 test_routes.py
```

### Expected Output
A properly fixed graph should show:
- Mall of America → Target Field: **20 stops** on Blue Line (no transfers)
- Total transit time: **~19 minutes**
- All algorithms find the same optimal path

## Rebuilding the Graph

If your graph has issues:

1. **Delete the old graph:**
```bash
rm transit_graph.pkl
```

2. **Rebuild from API:**
```bash
python3 graph_serializer.py
```

3. **Apply transfer penalty fix:**
```bash
python3 fix_transfer_penalty.py
```

## Common Issues

**"FileNotFoundError: transit_graph.pkl"**
- Run `graph_serializer.py` first to build the graph

**Routes showing unexpected transfers**
- Run `fix_transfer_penalty.py` to set proper transfer penalties

**API returns 403 errors**
- Confirm you're using `https://svc.metrotransit.org/` (not www.)
- Only query directions 0 and 1

**Algorithms find different paths**
- Check transfer penalties are set correctly (15 minutes)
- Verify transit times are calculated for all edges

## Authors

William Acosta Lora, Karla Martinez, Makol Chuol, Karim Amra, Dureti Gamada
Macalester College - Computer Science Department

## License

Macalester College