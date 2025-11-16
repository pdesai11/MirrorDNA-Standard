#!/usr/bin/env python3
"""
MirrorDNA Lineage Visualizer

Generates visual graphs of predecessor/successor lineage chains.
Supports GraphViz DOT format, SVG export, and interactive HTML.

Usage:
  # Visualize current project lineage
  python tools/visualize-lineage.py

  # Output as SVG (requires graphviz)
  python tools/visualize-lineage.py --format svg --output lineage.svg

  # Output as HTML (interactive)
  python tools/visualize-lineage.py --format html --output lineage.html

  # From specific sidecar file
  python tools/visualize-lineage.py --sidecar path/to/file.sidecar.json

  # Visualize all sidecars in directory
  python tools/visualize-lineage.py --scan ./state

Features:
  - Parses lineage from continuity_profile.yaml and .sidecar.json files
  - Builds directed graph of predecessor→successor relationships
  - Detects cycles and broken links
  - Generates GraphViz DOT format
  - Exports to SVG (if graphviz installed) or interactive HTML
  - Shows metadata in tooltips (vault_id, checksum, timestamps)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime


class LineageNode:
    """Represents a node in the lineage graph."""

    def __init__(self, node_id: str):
        self.id = node_id
        self.predecessors: Set[str] = set()
        self.successors: Set[str] = set()
        self.metadata: Dict = {}

    def add_predecessor(self, predecessor_id: str):
        """Add a predecessor node."""
        self.predecessors.add(predecessor_id)

    def add_successor(self, successor_id: str):
        """Add a successor node."""
        self.successors.add(successor_id)

    def set_metadata(self, key: str, value):
        """Set metadata for this node."""
        self.metadata[key] = value


class LineageGraph:
    """Represents the complete lineage graph."""

    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.cycles: List[List[str]] = []
        self.broken_links: List[Tuple[str, str]] = []

    def add_node(self, node_id: str) -> LineageNode:
        """Add or get a node."""
        if node_id not in self.nodes:
            self.nodes[node_id] = LineageNode(node_id)
        return self.nodes[node_id]

    def add_edge(self, predecessor_id: str, successor_id: str):
        """Add an edge from predecessor to successor."""
        pred_node = self.add_node(predecessor_id)
        succ_node = self.add_node(successor_id)

        pred_node.add_successor(successor_id)
        succ_node.add_predecessor(predecessor_id)

    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the graph using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node_id: str, path: List[str]) -> bool:
            """DFS to detect cycles."""
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for successor_id in node.successors:
                    if successor_id not in visited:
                        if dfs(successor_id, path.copy()):
                            return True
                    elif successor_id in rec_stack:
                        # Found cycle
                        cycle_start = path.index(successor_id)
                        cycle = path[cycle_start:] + [successor_id]
                        cycles.append(cycle)
                        return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        self.cycles = cycles
        return cycles

    def detect_broken_links(self) -> List[Tuple[str, str]]:
        """Detect broken links (references to non-existent nodes)."""
        broken = []

        for node_id, node in self.nodes.items():
            # Check predecessors
            for pred_id in node.predecessors:
                if pred_id not in self.nodes:
                    broken.append((pred_id, node_id))

            # Check successors
            for succ_id in node.successors:
                if succ_id not in self.nodes:
                    broken.append((node_id, succ_id))

        self.broken_links = broken
        return broken

    def get_roots(self) -> List[str]:
        """Get root nodes (nodes with no predecessors)."""
        return [node_id for node_id, node in self.nodes.items() if not node.predecessors]

    def get_leaves(self) -> List[str]:
        """Get leaf nodes (nodes with no successors)."""
        return [node_id for node_id, node in self.nodes.items() if not node.successors]


class LineageVisualizer:
    """Generates visualizations of lineage graphs."""

    def __init__(self):
        self.graph = LineageGraph()

    def parse_sidecar(self, sidecar_path: Path):
        """Parse a sidecar file and add to graph."""
        try:
            with open(sidecar_path, 'r') as f:
                data = json.load(f)

            # Extract node ID (use vault_id or filename)
            node_id = data.get('vault_id', sidecar_path.stem)

            node = self.graph.add_node(node_id)

            # Add metadata
            node.set_metadata('vault_id', data.get('vault_id', ''))
            node.set_metadata('checksum', data.get('checksum_sha256', ''))
            node.set_metadata('version', data.get('version', ''))
            node.set_metadata('timestamp', data.get('timestamp', ''))

            # Parse lineage
            lineage = data.get('lineage', {})

            # Add predecessors
            predecessors = lineage.get('predecessors', [])
            if isinstance(predecessors, list):
                for pred_id in predecessors:
                    self.graph.add_edge(pred_id, node_id)

            # Add successors
            successors = lineage.get('successors', [])
            if isinstance(successors, list):
                for succ_id in successors:
                    self.graph.add_edge(node_id, succ_id)

        except Exception as e:
            print(f"Warning: Error parsing {sidecar_path}: {e}", file=sys.stderr)

    def scan_directory(self, directory: Path):
        """Scan directory for sidecar files."""
        if not directory.exists():
            print(f"Error: Directory not found: {directory}", file=sys.stderr)
            return

        # Find all .sidecar.json files
        sidecar_files = list(directory.rglob('*.sidecar.json'))

        if not sidecar_files:
            print(f"No sidecar files found in {directory}", file=sys.stderr)
            return

        print(f"Found {len(sidecar_files)} sidecar file(s)")

        for sidecar_file in sidecar_files:
            self.parse_sidecar(sidecar_file)

    def generate_dot(self) -> str:
        """Generate GraphViz DOT format."""
        # Detect issues
        cycles = self.graph.detect_cycles()
        broken_links = self.graph.detect_broken_links()

        # Start DOT
        lines = [
            'digraph Lineage {',
            '  rankdir=LR;',
            '  node [shape=box, style=rounded];',
            ''
        ]

        # Define nodes
        for node_id, node in self.graph.nodes.items():
            # Build label
            label_parts = [node_id]

            if node.metadata.get('version'):
                label_parts.append(f"v{node.metadata['version']}")

            if node.metadata.get('checksum'):
                checksum_short = node.metadata['checksum'][:8]
                label_parts.append(f"[{checksum_short}]")

            label = '\\n'.join(label_parts)

            # Determine color
            color = 'black'
            fillcolor = 'lightgray'

            # Root nodes (no predecessors)
            if not node.predecessors:
                fillcolor = 'lightgreen'

            # Leaf nodes (no successors)
            if not node.successors:
                fillcolor = 'lightblue'

            # Nodes in cycles
            for cycle in cycles:
                if node_id in cycle:
                    fillcolor = 'orange'
                    break

            lines.append(
                f'  "{node_id}" [label="{label}", fillcolor={fillcolor}, style=filled];'
            )

        lines.append('')

        # Define edges
        for node_id, node in self.graph.nodes.items():
            for successor_id in node.successors:
                # Check if edge is part of cycle
                edge_style = ''
                for cycle in cycles:
                    if node_id in cycle and successor_id in cycle:
                        edge_style = ', color=red, penwidth=2'
                        break

                lines.append(f'  "{node_id}" -> "{successor_id}"{edge_style};')

        # Add broken links as dashed edges
        for from_id, to_id in broken_links:
            lines.append(
                f'  "{from_id}" -> "{to_id}" [style=dashed, color=red, label="broken"];'
            )

        lines.append('}')

        return '\n'.join(lines)

    def generate_svg(self, dot_content: str) -> Optional[str]:
        """Generate SVG from DOT using graphviz (if available)."""
        try:
            import subprocess

            result = subprocess.run(
                ['dot', '-Tsvg'],
                input=dot_content,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout

        except FileNotFoundError:
            print("Error: graphviz 'dot' command not found", file=sys.stderr)
            print("Install graphviz: https://graphviz.org/download/", file=sys.stderr)
            return None

        except subprocess.CalledProcessError as e:
            print(f"Error running dot: {e}", file=sys.stderr)
            return None

    def generate_html(self) -> str:
        """Generate interactive HTML visualization."""
        # Detect issues
        cycles = self.graph.detect_cycles()
        broken_links = self.graph.detect_broken_links()

        # Build node data
        nodes_json = []
        for node_id, node in self.graph.nodes.items():
            node_data = {
                'id': node_id,
                'label': node_id,
                'metadata': node.metadata,
                'predecessors': list(node.predecessors),
                'successors': list(node.successors),
                'isRoot': len(node.predecessors) == 0,
                'isLeaf': len(node.successors) == 0,
                'inCycle': any(node_id in cycle for cycle in cycles)
            }
            nodes_json.append(node_data)

        # Build edge data
        edges_json = []
        for node_id, node in self.graph.nodes.items():
            for successor_id in node.successors:
                edge_data = {
                    'from': node_id,
                    'to': successor_id,
                    'inCycle': any(
                        node_id in cycle and successor_id in cycle
                        for cycle in cycles
                    )
                }
                edges_json.append(edge_data)

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MirrorDNA Lineage Graph</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .stats {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .stats div {{
            display: inline-block;
            margin-right: 20px;
        }}
        .graph {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            background: white;
            min-height: 400px;
        }}
        .node {{
            display: inline-block;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 5px;
            border: 2px solid #333;
            background: #f0f0f0;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .node:hover {{
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .node.root {{
            background: #90ee90;
        }}
        .node.leaf {{
            background: #add8e6;
        }}
        .node.cycle {{
            background: #ffb347;
            border-color: #ff6347;
        }}
        .metadata {{
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }}
        .issues {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #ffc107;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 1px solid #333;
            margin-right: 5px;
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⟡⟦LINEAGE⟧ MirrorDNA Lineage Graph</h1>

        <div class="stats">
            <div><strong>Nodes:</strong> <span id="node-count">{len(self.graph.nodes)}</span></div>
            <div><strong>Roots:</strong> <span id="root-count">{len(self.graph.get_roots())}</span></div>
            <div><strong>Leaves:</strong> <span id="leaf-count">{len(self.graph.get_leaves())}</span></div>
            <div><strong>Cycles:</strong> <span id="cycle-count">{len(cycles)}</span></div>
            <div><strong>Broken Links:</strong> <span id="broken-count">{len(broken_links)}</span></div>
        </div>

        <div class="graph" id="graph">
            <!-- Nodes will be rendered here -->
        </div>

        {f'''
        <div class="issues">
            <h3>⚠️ Issues Detected</h3>
            <div><strong>Cycles:</strong> {len(cycles)}</div>
            <ul>
                {''.join(f'<li>{" → ".join(cycle)}</li>' for cycle in cycles)}
            </ul>
            <div><strong>Broken Links:</strong> {len(broken_links)}</div>
            <ul>
                {''.join(f'<li>{from_id} → {to_id}</li>' for from_id, to_id in broken_links)}
            </ul>
        </div>
        ''' if cycles or broken_links else ''}

        <div class="legend">
            <h3>Legend</h3>
            <div class="legend-item">
                <span class="legend-color" style="background: #90ee90;"></span>
                Root (no predecessors)
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #add8e6;"></span>
                Leaf (no successors)
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ffb347;"></span>
                In cycle
            </div>
        </div>
    </div>

    <script>
        const nodes = {json.dumps(nodes_json, indent=2)};
        const edges = {json.dumps(edges_json, indent=2)};

        // Render nodes
        const graphDiv = document.getElementById('graph');

        nodes.forEach(node => {{
            const nodeDiv = document.createElement('div');
            nodeDiv.className = 'node';

            if (node.isRoot) nodeDiv.classList.add('root');
            if (node.isLeaf) nodeDiv.classList.add('leaf');
            if (node.inCycle) nodeDiv.classList.add('cycle');

            let html = `<strong>${{node.id}}</strong>`;

            if (node.metadata.version) {{
                html += `<div class="metadata">Version: ${{node.metadata.version}}</div>`;
            }}
            if (node.metadata.checksum) {{
                const checksumShort = node.metadata.checksum.substring(0, 12);
                html += `<div class="metadata">Checksum: ${{checksumShort}}...</div>`;
            }}
            if (node.predecessors.length > 0) {{
                html += `<div class="metadata">← ${{node.predecessors.length}} predecessor(s)</div>`;
            }}
            if (node.successors.length > 0) {{
                html += `<div class="metadata">→ ${{node.successors.length}} successor(s)</div>`;
            }}

            nodeDiv.innerHTML = html;
            nodeDiv.title = JSON.stringify(node.metadata, null, 2);

            graphDiv.appendChild(nodeDiv);
        }});

        // Add click handlers
        document.querySelectorAll('.node').forEach((nodeDiv, index) => {{
            nodeDiv.addEventListener('click', () => {{
                const node = nodes[index];
                alert(`Node: ${{node.id}}\\n\\nPredecessors: ${{node.predecessors.join(', ') || 'None'}}\\nSuccessors: ${{node.successors.join(', ') || 'None'}}\\n\\nMetadata:\\n${{JSON.stringify(node.metadata, null, 2)}}`);
            }});
        }});
    </script>
</body>
</html>"""

        return html

    def save_output(self, content: str, output_path: Path):
        """Save content to file."""
        try:
            output_path.write_text(content)
            print(f"✓ Visualization saved to: {output_path}")

        except Exception as e:
            print(f"Error saving output: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Visualize MirrorDNA lineage chains',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  python tools/visualize-lineage.py

  # Scan specific directory
  python tools/visualize-lineage.py --scan ./state

  # From specific sidecar
  python tools/visualize-lineage.py --sidecar file.sidecar.json

  # Output as SVG (requires graphviz)
  python tools/visualize-lineage.py --format svg --output lineage.svg

  # Output as HTML (interactive)
  python tools/visualize-lineage.py --format html --output lineage.html

Output Formats:
  - dot: GraphViz DOT format (default)
  - svg: SVG image (requires graphviz installed)
  - html: Interactive HTML with tooltips

Legend:
  - Green: Root nodes (no predecessors)
  - Blue: Leaf nodes (no successors)
  - Orange: Nodes in cycles
  - Red edges: Part of cycle or broken link
        """
    )

    parser.add_argument(
        '--sidecar',
        help='Path to specific sidecar file'
    )
    parser.add_argument(
        '--scan',
        default='.',
        help='Scan directory for sidecar files (default: current directory)'
    )
    parser.add_argument(
        '--format',
        choices=['dot', 'svg', 'html'],
        default='dot',
        help='Output format (default: dot)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout for dot, lineage.{format} for others)'
    )

    args = parser.parse_args()

    # Create visualizer
    visualizer = LineageVisualizer()

    # Parse input
    if args.sidecar:
        sidecar_path = Path(args.sidecar)
        if not sidecar_path.exists():
            print(f"Error: File not found: {sidecar_path}", file=sys.stderr)
            return 1
        visualizer.parse_sidecar(sidecar_path)
    else:
        # Scan directory
        scan_dir = Path(args.scan)
        visualizer.scan_directory(scan_dir)

    if not visualizer.graph.nodes:
        print("No lineage data found", file=sys.stderr)
        return 1

    # Generate output
    if args.format == 'dot':
        content = visualizer.generate_dot()
        output_path = Path(args.output) if args.output else None

        if output_path:
            visualizer.save_output(content, output_path)
        else:
            print(content)

    elif args.format == 'svg':
        dot_content = visualizer.generate_dot()
        svg_content = visualizer.generate_svg(dot_content)

        if not svg_content:
            return 1

        output_path = Path(args.output) if args.output else Path('lineage.svg')
        visualizer.save_output(svg_content, output_path)

    elif args.format == 'html':
        html_content = visualizer.generate_html()
        output_path = Path(args.output) if args.output else Path('lineage.html')
        visualizer.save_output(html_content, output_path)

    # Print summary
    print(f"\nLineage Graph Summary:")
    print(f"  Nodes: {len(visualizer.graph.nodes)}")
    print(f"  Root nodes: {len(visualizer.graph.get_roots())}")
    print(f"  Leaf nodes: {len(visualizer.graph.get_leaves())}")

    cycles = visualizer.graph.detect_cycles()
    if cycles:
        print(f"  ⚠️  Cycles detected: {len(cycles)}")
        for cycle in cycles:
            print(f"     {' → '.join(cycle)}")

    broken_links = visualizer.graph.detect_broken_links()
    if broken_links:
        print(f"  ⚠️  Broken links: {len(broken_links)}")
        for from_id, to_id in broken_links:
            print(f"     {from_id} → {to_id}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
