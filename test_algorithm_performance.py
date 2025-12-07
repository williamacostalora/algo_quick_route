"""
Comprehensive Algorithm Performance Testing Suite

Tests all 4 algorithms across multiple scenarios to compare:
- Execution time (time complexity)
- Nodes explored (space/search efficiency)
- Path optimality
- Scalability with distance

This generates data for your research paper.
"""

import pickle
import time
import statistics
from typing import List, Dict
import matplotlib.pyplot as plt


class AlgorithmTester:
    """Test and compare pathfinding algorithms."""

    def __init__(self, graph):
        self.graph = graph
        self.results = []

    def run_comprehensive_tests(self):
        """Run tests across various route types and distances."""

        print("=" * 80)
        print("COMPREHENSIVE ALGORITHM PERFORMANCE TESTING")
        print("=" * 80)

        # Define test scenarios of varying complexity
        test_scenarios = [
            # SHORT DISTANCE (1-5 stops)
            {
                'category': 'Short Distance',
                'name': 'Adjacent Stops on Blue Line',
                'start': 30,  # Mall of America
                'end': 2,  # 30th Ave Station
                'expected_stops': 2,
                'description': 'Minimal path, 1 segment'
            },
            {
                'category': 'Short Distance',
                'name': 'Short Blue Line Trip',
                'start': 30,  # Mall of America
                'end': 13,  # American Blvd
                'expected_stops': 4,
                'description': '3 segments'
            },

            # MEDIUM DISTANCE (5-15 stops)
            {
                'category': 'Medium Distance',
                'name': 'Airport to Downtown',
                'start': 45,  # Terminal 1
                'end': 25,  # Government Plaza
                'expected_stops': 10,
                'description': 'Half of Blue Line'
            },
            {
                'category': 'Medium Distance',
                'name': 'Green Line Segment',
                'start': 52,  # West Bank
                'end': 39,  # Snelling Ave
                'expected_stops': 8,
                'description': 'Green Line through campus'
            },

            # LONG DISTANCE (15+ stops)
            {
                'category': 'Long Distance',
                'name': 'Full Blue Line',
                'start': 30,  # Mall of America
                'end': 44,  # Target Field Platform 2
                'expected_stops': 20,
                'description': 'Complete Blue Line route'
            },
            {
                'category': 'Long Distance',
                'name': 'Full Green Line',
                'start': 52,  # West Bank
                'end': 48,  # Union Depot
                'expected_stops': 18,
                'description': 'Complete Green Line route'
            },

            # MULTI-ROUTE (requires transfer)
            {
                'category': 'Multi-Route',
                'name': 'Cross-City with Transfer',
                'start': 30,  # Mall of America (Blue)
                'end': 48,  # Union Depot (Green)
                'expected_stops': 25,
                'description': 'Requires Blue→Green transfer'
            },
            {
                'category': 'Multi-Route',
                'name': 'Complex Transfer Route',
                'start': 26,  # Grand Ave (Route 63)
                'end': 43,  # Target Field (Blue)
                'expected_stops': 15,
                'description': 'Bus→Rail transfer'
            },
        ]

        all_results = []

        for scenario in test_scenarios:
            print(f"\n{'=' * 80}")
            print(f"Testing: {scenario['name']}")
            print(f"Category: {scenario['category']}")
            print(f"Description: {scenario['description']}")
            print(f"{'=' * 80}")

            scenario_results = self.test_scenario(
                scenario['start'],
                scenario['end'],
                scenario['name'],
                scenario['category']
            )

            all_results.extend(scenario_results)

        self.results = all_results
        return all_results

    def test_scenario(self, start_id: int, end_id: int,
                      name: str, category: str) -> List[Dict]:
        """Test all algorithms on a single scenario."""

        results = []

        # Get stop names
        start_stop = self.graph.stops[start_id - 1]
        end_stop = self.graph.stops[end_id - 1]

        print(f"\nFrom: {start_stop.get_name()}")
        print(f"To:   {end_stop.get_name()}")
        print("\nRunning algorithms:")

        # Test each algorithm
        algorithms = [
            ('Dijkstra', lambda: self.graph.dijkstra(start_stop.get_stop_id(), end_stop.get_stop_id())),
            ('A*', lambda: self.graph.a_star(start_stop.get_stop_id(), end_stop.get_stop_id())),
            ('Floyd-Warshall', lambda: self.graph.floyd_warshall(start_stop.get_stop_id(), end_stop.get_stop_id())),
            ('Weighted A* (1.5)',
             lambda: self.graph.weighted_a_star(start_stop.get_stop_id(), end_stop.get_stop_id(), 1.5)),
             ('BFS', lambda: self.graph.BFS(start_stop.get_stop_id(), end_stop.get_stop_id(), 1.5))
        ]

        for algo_name, algo_func in algorithms:
            # Run multiple times for accurate timing
            times = []
            path_result = None
            metrics_result = None

            for _ in range(5):  # 5 runs for averaging
                path, total_time, metrics = algo_func()
                times.append(metrics['execution_time'])
                if path_result is None:
                    path_result = path
                    metrics_result = metrics

            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0

            result = {
                'scenario': name,
                'category': category,
                'algorithm': algo_name,
                'avg_execution_time': avg_time,
                'std_dev': std_dev,
                'min_time': min(times),
                'max_time': max(times),
                'nodes_explored': metrics_result['nodes_explored'],
                'path_length': len(path_result),
                'transit_time': metrics_result['total_transit_time'],
            }

            results.append(result)

            print(f"  {algo_name:20} | "
                  f"Time: {avg_time * 1000:.3f}ms ± {std_dev * 1000:.3f}ms | "
                  f"Nodes: {metrics_result['nodes_explored']:6} | "
                  f"Path: {len(path_result):2} stops")

        return results

    def generate_comparison_report(self):
        """Generate detailed comparison report."""

        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON REPORT")
        print("=" * 80)

        # Group by category
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)

        for category, results in categories.items():
            print(f"\n{category.upper()}")
            print("-" * 80)

            # Average performance by algorithm in this category
            algo_stats = {}
            for result in results:
                algo = result['algorithm']
                if algo not in algo_stats:
                    algo_stats[algo] = {
                        'times': [],
                        'nodes': [],
                        'paths': []
                    }
                algo_stats[algo]['times'].append(result['avg_execution_time'])
                algo_stats[algo]['nodes'].append(result['nodes_explored'])
                algo_stats[algo]['paths'].append(result['path_length'])

            print(f"\n{'Algorithm':<20} {'Avg Time (ms)':<15} {'Avg Nodes':<12} {'Avg Path Length':<15}")
            print("-" * 80)

            for algo in sorted(algo_stats.keys()):
                avg_time = statistics.mean(algo_stats[algo]['times']) * 1000
                avg_nodes = statistics.mean(algo_stats[algo]['nodes'])
                avg_path = statistics.mean(algo_stats[algo]['paths'])

                print(f"{algo:<20} {avg_time:>10.3f}      {avg_nodes:>8.0f}    {avg_path:>10.1f}")

        # Overall winner analysis
        print("\n" + "=" * 80)
        print("OVERALL ANALYSIS")
        print("=" * 80)

        # Fastest algorithm
        algo_times = {}
        for result in self.results:
            algo = result['algorithm']
            if algo not in algo_times:
                algo_times[algo] = []
            algo_times[algo].append(result['avg_execution_time'])

        print("\nAverage Execution Time (across all scenarios):")
        for algo in sorted(algo_times.keys(), key=lambda x: statistics.mean(algo_times[x])):
            avg_time = statistics.mean(algo_times[algo]) * 1000
            print(f"  {algo:<20} {avg_time:.3f} ms")

        # Most efficient (nodes explored)
        algo_nodes = {}
        for result in self.results:
            algo = result['algorithm']
            if algo not in algo_nodes:
                algo_nodes[algo] = []
            algo_nodes[algo].append(result['nodes_explored'])

        print("\nAverage Nodes Explored (search efficiency):")
        for algo in sorted(algo_nodes.keys(), key=lambda x: statistics.mean(algo_nodes[x])):
            avg_nodes = statistics.mean(algo_nodes[algo])
            print(f"  {algo:<20} {avg_nodes:.0f} nodes")

    def generate_visualizations(self, output_dir='./'):
        """Generate comparison charts."""

        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80)

        # Create figure with 4 subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Pathfinding Algorithm Performance Comparison',
                     fontsize=16, fontweight='bold')

        # Get data by algorithm
        algorithms = ['Dijkstra', 'A*', 'Floyd-Warshall', 'Weighted A* (1.5)', 'BFS']

        # 1. Execution Time by Category
        ax1 = axes[0, 0]
        categories = ['Short Distance', 'Medium Distance', 'Long Distance', 'Multi-Route']

        for algo in algorithms:
            times_by_cat = []
            for cat in categories:
                cat_times = [r['avg_execution_time'] * 1000
                             for r in self.results
                             if r['algorithm'] == algo and r['category'] == cat]
                times_by_cat.append(statistics.mean(cat_times) if cat_times else 0)

            ax1.plot(categories, times_by_cat, marker='o', label=algo, linewidth=2)

        ax1.set_xlabel('Route Category', fontweight='bold')
        ax1.set_ylabel('Execution Time (ms)', fontweight='bold')
        ax1.set_title('Execution Time by Route Category')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=15, ha='right')

        # 2. Nodes Explored
        ax2 = axes[0, 1]
        algo_nodes = {}
        for algo in algorithms:
            nodes = [r['nodes_explored'] for r in self.results if r['algorithm'] == algo]
            algo_nodes[algo] = statistics.mean(nodes)

        bars = ax2.bar(range(len(algorithms)),
                       [algo_nodes[algo] for algo in algorithms],
                       color=['skyblue', 'lightcoral', 'lightgreen', 'plum'])
        ax2.set_xticks(range(len(algorithms)))
        ax2.set_xticklabels(algorithms, rotation=15, ha='right')
        ax2.set_ylabel('Average Nodes Explored', fontweight='bold')
        ax2.set_title('Search Space Efficiency')
        ax2.grid(True, axis='y', alpha=0.3)

        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}', ha='center', va='bottom')

        # 3. Execution Time vs Path Length (scatter)
        ax3 = axes[1, 0]
        colors = {'Dijkstra': 'blue', 'A*': 'red', 'Floyd-Warshall': 'green',
                  'Weighted A* (1.5)': 'purple', 'BFS': 'orange'}

        for algo in algorithms:
            algo_results = [r for r in self.results if r['algorithm'] == algo]
            path_lengths = [r['path_length'] for r in algo_results]
            exec_times = [r['avg_execution_time'] * 1000 for r in algo_results]

            ax3.scatter(path_lengths, exec_times,
                        label=algo, color=colors[algo], alpha=0.6, s=100)

        ax3.set_xlabel('Path Length (stops)', fontweight='bold')
        ax3.set_ylabel('Execution Time (ms)', fontweight='bold')
        ax3.set_title('Scalability: Time vs Path Complexity')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Average Execution Time Comparison (actual times, not relative)
        ax4 = axes[1, 1]

        # Calculate average execution time for each algorithm
        avg_times = []
        for algo in algorithms:
            algo_avg = statistics.mean([r['avg_execution_time'] * 1000  # Convert to ms
                                        for r in self.results
                                        if r['algorithm'] == algo])
            avg_times.append(algo_avg)
            # Debug: print what we're seeing
            print(f"DEBUG: {algo} average time = {algo_avg:.3f} ms")

        # Color code: green for fastest, red for slowest, others in between
        min_time = min(avg_times)
        max_time = max(avg_times)
        print(f"\nDEBUG: Fastest time = {min_time:.3f} ms, Slowest time = {max_time:.3f} ms")

        colors_bars = []
        for i, t in enumerate(avg_times):
            if t == min_time:
                colors_bars.append('lightgreen')  # Fastest
                print(f"DEBUG: {algorithms[i]} is FASTEST")
            elif t == max_time:
                colors_bars.append('lightcoral')  # Slowest
                print(f"DEBUG: {algorithms[i]} is SLOWEST")
            else:
                colors_bars.append('skyblue')  # In between

        bars = ax4.bar(range(len(algorithms)), avg_times, color=colors_bars)
        ax4.set_xticks(range(len(algorithms)))
        ax4.set_xticklabels(algorithms, rotation=15, ha='right')
        ax4.set_ylabel('Average Execution Time (ms)', fontweight='bold')
        ax4.set_title('Average Execution Time Comparison')
        ax4.grid(True, axis='y', alpha=0.3)

        # Add value labels with ranking
        for i, bar in enumerate(bars):
            height = bar.get_height()
            # Add the actual time value
            ax4.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.3f} ms', ha='center', va='bottom', fontsize=9)

        # Add legend explaining colors
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightgreen', label='Fastest'),
            Patch(facecolor='skyblue', label='Medium'),
            Patch(facecolor='lightcoral', label='Slowest')
        ]
        ax4.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()

        # Save
        output_file = output_dir + 'algorithm_performance_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_file}")

        plt.close()

    def export_latex_table(self, output_dir='./'):
        """Export results as LaTeX table for paper."""

        output_file = output_dir + 'performance_table.tex'

        with open(output_file, 'w') as f:
            f.write("\\begin{table}[H]\n")
            f.write("\\centering\n")
            f.write("\\caption{Algorithm Performance Comparison by Route Category}\n")
            f.write("\\label{tab:performance}\n")
            f.write("\\begin{tabular}{|l|l|r|r|r|}\n")
            f.write("\\hline\n")
            f.write(
                "\\textbf{Category} & \\textbf{Algorithm} & \\textbf{Time (ms)} & \\textbf{Nodes} & \\textbf{Path} \\\\\n")
            f.write("\\hline\n")

            categories = ['Short Distance', 'Medium Distance', 'Long Distance', 'Multi-Route']
            algorithms = ['Dijkstra', 'A*', 'Floyd-Warshall', 'Weighted A* (1.5)', 'BFS']

            for category in categories:
                cat_results = [r for r in self.results if r['category'] == category]

                for i, algo in enumerate(algorithms):
                    algo_results = [r for r in cat_results if r['algorithm'] == algo]
                    if algo_results:
                        avg_time = statistics.mean([r['avg_execution_time'] for r in algo_results]) * 1000
                        avg_nodes = statistics.mean([r['nodes_explored'] for r in algo_results])
                        avg_path = statistics.mean([r['path_length'] for r in algo_results])

                        if i == 0:
                            f.write(f"{category} & {algo} & {avg_time:.3f} & {int(avg_nodes)} & {avg_path:.1f} \\\\\n")
                        else:
                            f.write(f" & {algo} & {avg_time:.3f} & {int(avg_nodes)} & {avg_path:.1f} \\\\\n")

                if category != categories[-1]:
                    f.write("\\hline\n")

            f.write("\\hline\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"✓ Saved LaTeX table: {output_file}")


def main():
    """Run comprehensive algorithm testing."""

    # Load graph
    print("Loading transit graph...")
    with open('graph_data.pkl', 'rb') as f:
        graph = pickle.load(f)

    print(f"Loaded graph: {len(graph.stops)} stops\n")

    # Create tester
    tester = AlgorithmTester(graph)

    # Run comprehensive tests
    results = tester.run_comprehensive_tests()

    # Generate report
    tester.generate_comparison_report()

    # Generate visualizations
    tester.generate_visualizations()

    # Export LaTeX table
    tester.export_latex_table()

    print("\n" + "=" * 80)
    print(" TESTING COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - algorithm_performance_comparison.png")
    print("  - performance_table.tex")
    print("\nUse these for your research paper!")


if __name__ == "__main__":
    main()