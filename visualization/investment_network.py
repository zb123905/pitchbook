"""
Investment Network Graph Generator
Creates network visualizations of investment relationships
"""
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from visualization.chart_config import setup_chinese_font, save_chart, get_color_for_label

logger = logging.getLogger(__name__)


class InvestmentNetworkGenerator:
    """
    Generate investment relationship network graphs

    Creates directed graphs showing:
    - Investor → Company relationships
    - Investment amounts (edge weights)
    - Deal stages (edge labels)
    - Company/Investor importance (node sizes)
    """

    def __init__(self, figsize: Tuple[int, int] = (16, 12)):
        """
        Initialize network generator

        Args:
            figsize: Figure size (width, height) in inches
        """
        self.figsize = figsize
        setup_chinese_font()

    def generate_network_graph(
        self,
        relations: List[Dict],
        output_path: Optional[str] = None,
        layout: str = 'spring',
        min_amount: Optional[float] = None,
        top_n: int = 50
    ) -> plt.Figure:
        """
        Generate investment network graph

        Args:
            relations: List of investment relations
            output_path: Optional path to save the chart
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai', 'random')
            min_amount: Minimum investment amount to include (filters small deals)
            top_n: Maximum number of nodes to display

        Returns:
            matplotlib Figure object
        """
        logger.info(f"Generating investment network graph with {len(relations)} relations")

        # Filter relations
        filtered_relations = self._filter_relations(relations, min_amount)

        if not filtered_relations:
            logger.warning("No relations to display after filtering")
            return self._create_empty_graph()

        # Create directed graph
        G = self._build_graph(filtered_relations)

        # Limit to top N nodes if needed
        if len(G.nodes()) > top_n:
            G = self._get_top_nodes_subgraph(G, top_n)

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)

        # Choose layout
        pos = self._get_layout(G, layout)

        # Draw nodes
        self._draw_nodes(G, pos, ax)

        # Draw edges
        self._draw_edges(G, pos, ax)

        # Draw labels
        self._draw_labels(G, pos, ax)

        # Styling
        ax.set_title('投资关系网络图 (Investment Network)', fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')

        # Add legend
        self._add_legend(ax)

        plt.tight_layout()

        # Save if path provided
        if output_path:
            save_chart(fig, output_path)

        return fig

    def _filter_relations(self, relations: List[Dict], min_amount: Optional[float]) -> List[Dict]:
        """Filter relations by minimum amount"""
        if min_amount is None:
            return relations

        filtered = []
        for rel in relations:
            amount = rel.get('amount', {})
            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            if amount_value >= min_amount:
                filtered.append(rel)

        logger.info(f"Filtered to {len(filtered)} relations (min_amount: {min_amount})")
        return filtered

    def _build_graph(self, relations: List[Dict]) -> nx.DiGraph:
        """Build NetworkX directed graph from relations"""
        G = nx.DiGraph()

        for rel in relations:
            if rel.get('type') != 'investment':
                continue

            investor = rel.get('investor', '')
            target = rel.get('target', '')
            stage = rel.get('stage', '')
            amount = rel.get('amount', {})

            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
                currency = amount.get('currency', 'USD')
            else:
                amount_value = 0
                currency = 'USD'

            # Add edge
            if investor and target:
                G.add_edge(
                    investor,
                    target,
                    weight=amount_value,
                    stage=stage,
                    currency=currency,
                    relation=rel
                )

        logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G

    def _get_top_nodes_subgraph(self, G: nx.DiGraph, top_n: int) -> nx.DiGraph:
        """Get subgraph with top N nodes by degree"""
        # Calculate node importance (degree)
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_node_names = [node[0] for node in top_nodes]

        # Create subgraph
        subgraph = G.subgraph(top_node_names).copy()
        logger.info(f"Limited to top {top_n} nodes")
        return subgraph

    def _get_layout(self, G: nx.DiGraph, layout: str) -> dict:
        """Get node positions for specified layout"""
        if layout == 'spring':
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        elif layout == 'random':
            pos = nx.random_layout(G, seed=42)
        else:
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

        return pos

    def _draw_nodes(self, G: nx.DiGraph, pos: dict, ax: plt.Axes):
        """Draw graph nodes"""
        # Calculate node sizes based on importance
        degrees = dict(G.degree())
        max_degree = max(degrees.values()) if degrees else 1

        # Base size + scaled by degree
        node_sizes = [500 + (degrees[node] / max_degree) * 2000 for node in G.nodes()]

        # Node colors based on type (investor vs company)
        node_colors = []
        for node in G.nodes():
            # Check if node has outgoing edges (is an investor)
            if G.out_degree(node) > 0 and G.in_degree(node) == 0:
                node_colors.append('#FF6B6B')  # Red for investors
            else:
                node_colors.append('#4ECDC4')  # Teal for companies

        # Draw nodes
        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.8,
            edgecolors='white',
            linewidths=2,
            ax=ax
        )

    def _draw_edges(self, G: nx.DiGraph, pos: dict, ax: plt.Axes):
        """Draw graph edges"""
        # Edge widths based on investment amount
        edges = G.edges(data=True)
        max_weight = max([data.get('weight', 0) for _, _, data in edges]) if edges else 1

        edge_widths = []
        edge_colors = []

        for _, _, data in edges:
            weight = data.get('weight', 0)
            # Scale width: base 1 + up to 5 more based on amount
            width = 1 + min(5, (weight / max_weight) * 5) if max_weight > 0 else 1
            edge_widths.append(width)

            # Color by stage
            stage = data.get('stage', '')
            edge_colors.append(get_color_for_label(stage, 'deal_stage'))

        # Draw edges
        nx.draw_networkx_edges(
            G,
            pos,
            width=edge_widths,
            edge_color=edge_colors,
            alpha=0.6,
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            connectionstyle='arc3,rad=0.1',
            ax=ax
        )

    def _draw_labels(self, G: nx.DiGraph, pos: dict, ax: plt.Axes):
        """Draw node labels"""
        # Only show labels for important nodes to avoid clutter
        degrees = dict(G.degree())
        max_degree = max(degrees.values()) if degrees else 1

        # Show labels for nodes with degree > 1 or top 20% by degree
        threshold = max(2, max_degree * 0.8)
        labels_to_show = {
            node: node
            for node, degree in degrees.items()
            if degree >= threshold or degree == max_degree
        }

        nx.draw_networkx_labels(
            G,
            pos,
            labels=labels_to_show,
            font_size=9,
            font_weight='bold',
            ax=ax
        )

        # Add edge labels for large deals
        edge_labels = {}
        for investor, target, data in G.edges(data=True):
            amount = data.get('weight', 0)
            stage = data.get('stage', '')
            if amount > 10000000:  # Only show amounts > $10M
                # Format amount
                if amount >= 1e9:
                    amount_str = f"${amount/1e9:.1f}B"
                elif amount >= 1e6:
                    amount_str = f"${amount/1e6:.1f}M"
                else:
                    amount_str = f"${amount/1e3:.0f}K"

                label = amount_str
                if stage:
                    label += f"\n{stage}"

                edge_labels[(investor, target)] = label

        if edge_labels:
            nx.draw_networkx_edge_labels(
                G,
                pos,
                edge_labels=edge_labels,
                font_size=7,
                ax=ax
            )

    def _add_legend(self, ax: plt.Axes):
        """Add legend to the graph"""
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor='#FF6B6B', label='投资机构 (Investor)'),
            Patch(facecolor='#4ECDC4', label='被投公司 (Company)')
        ]

        ax.legend(
            handles=legend_elements,
            loc='upper right',
            fontsize=10,
            framealpha=0.9
        )

    def _create_empty_graph(self) -> plt.Figure:
        """Create empty graph when no data"""
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.text(0.5, 0.5, '暂无投资关系数据\nNo investment relationship data',
                ha='center', va='center', fontsize=14, color='gray')
        ax.set_title('投资关系网络图 (Investment Network)', fontsize=16, fontweight='bold')
        ax.axis('off')
        return fig


# Demo and testing
if __name__ == "__main__":
    # Test data
    test_relations = [
        {
            'type': 'investment',
            'investor': '红杉资本',
            'target': '字节跳动',
            'stage': 'C轮',
            'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
            'date': '2024-03-15',
            'confidence': 0.9
        },
        {
            'type': 'investment',
            'investor': 'Sequoia Capital',
            'target': 'ByteDance',
            'stage': 'Series C',
            'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
            'date': '2024-03-15',
            'confidence': 0.9
        },
        {
            'type': 'investment',
            'investor': 'Hillhouse Capital',
            'target': 'ByteDance',
            'stage': 'Series C',
            'amount': {'amount': 500000000, 'currency': 'USD', 'normalized': '$500M'},
            'date': '2024-03-15',
            'confidence': 0.9
        },
        {
            'type': 'investment',
            'investor': '创新工场',
            'target': '快手',
            'stage': '种子轮',
            'amount': {'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'},
            'date': '2024-01-01',
            'confidence': 0.8
        },
    ]

    generator = InvestmentNetworkGenerator()

    print("="*70)
    print("Investment Network Graph Generator Test")
    print("="*70)

    fig = generator.generate_network_graph(
        test_relations,
        output_path='E:/pitch/数据储存/temp_charts/test_network.png'
    )

    print("\n✓ Network graph generated")
    print(f"  Nodes: Investment relationships visualized")
    print(f"  Layout: spring layout with node sizing by importance")
    print(f"  Saved: test_network.png")

    plt.close(fig)
