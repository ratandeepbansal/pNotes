"""Knowledge graph visualization for note connections."""
import networkx as nx
from pyvis.network import Network
from typing import Dict, List, Optional
import streamlit.components.v1 as components
from pathlib import Path

from ..db.metadata import MetadataDB


class KnowledgeGraphBuilder:
    """Build and visualize knowledge graphs from notes."""

    def __init__(self, metadata_db: Optional[MetadataDB] = None):
        """
        Initialize knowledge graph builder.

        Args:
            metadata_db: MetadataDB instance
        """
        self.metadata_db = metadata_db or MetadataDB()

    def build_graph(self, similarity_threshold: float = 0.7) -> nx.Graph:
        """
        Build a NetworkX graph from notes.

        Args:
            similarity_threshold: Minimum similarity for creating edges

        Returns:
            NetworkX graph
        """
        G = nx.Graph()

        # Get all notes
        all_notes = self.metadata_db.get_all_notes()

        # Add nodes
        for note_id, note_data in all_notes:
            title = note_data.get('title', 'Untitled')
            tags = note_data.get('tags', '')

            # Parse tags
            tag_list = []
            if tags:
                tag_list = tags.split(',') if isinstance(tags, str) else tags
                tag_list = [tag.strip() for tag in tag_list if tag.strip()]

            G.add_node(
                note_id,
                title=title,
                tags=tag_list,
                label=title[:30] + '...' if len(title) > 30 else title
            )

        # Add edges based on shared tags
        nodes_list = list(G.nodes(data=True))
        for i, (note_id_1, data_1) in enumerate(nodes_list):
            tags_1 = set(data_1.get('tags', []))
            if not tags_1:
                continue

            for note_id_2, data_2 in nodes_list[i + 1:]:
                tags_2 = set(data_2.get('tags', []))
                if not tags_2:
                    continue

                # Calculate Jaccard similarity
                intersection = len(tags_1 & tags_2)
                union = len(tags_1 | tags_2)

                if union > 0:
                    similarity = intersection / union
                    if similarity >= similarity_threshold:
                        G.add_edge(
                            note_id_1,
                            note_id_2,
                            weight=similarity,
                            shared_tags=list(tags_1 & tags_2)
                        )

        return G

    def create_pyvis_graph(
        self,
        G: nx.Graph,
        height: str = "750px",
        width: str = "100%",
        notebook: bool = False
    ) -> Network:
        """
        Create an interactive Pyvis network from NetworkX graph.

        Args:
            G: NetworkX graph
            height: Height of visualization
            width: Width of visualization
            notebook: Whether running in Jupyter notebook

        Returns:
            Pyvis Network object
        """
        net = Network(height=height, width=width, notebook=notebook, bgcolor="#222222", font_color="white")

        # Configure physics
        net.barnes_hut(
            gravity=-8000,
            central_gravity=0.3,
            spring_length=250,
            spring_strength=0.001,
            damping=0.09,
            overlap=0
        )

        # Add nodes with colors based on tag count
        for node, data in G.nodes(data=True):
            tags = data.get('tags', [])
            num_tags = len(tags)

            # Color nodes by tag count
            if num_tags == 0:
                color = "#888888"  # Gray for no tags
            elif num_tags <= 2:
                color = "#4A90E2"  # Blue
            elif num_tags <= 4:
                color = "#50C878"  # Green
            else:
                color = "#FF6B6B"  # Red for many tags

            title_html = f"<b>{data['title']}</b><br>Tags: {', '.join(tags) if tags else 'None'}"

            net.add_node(
                node,
                label=data.get('label', data['title']),
                title=title_html,
                color=color,
                size=15 + num_tags * 3
            )

        # Add edges
        for edge in G.edges(data=True):
            source, target, data = edge
            weight = data.get('weight', 0.5)
            shared = data.get('shared_tags', [])

            net.add_edge(
                source,
                target,
                value=weight * 5,  # Edge thickness
                title=f"Shared tags: {', '.join(shared)}" if shared else "Connected"
            )

        return net

    def save_html(self, net: Network, output_path: str = "knowledge_graph.html"):
        """
        Save the network to an HTML file.

        Args:
            net: Pyvis Network object
            output_path: Path to save HTML file

        Returns:
            Path to saved file
        """
        net.save_graph(output_path)
        return output_path

    def render_in_streamlit(self, html_path: str, height: int = 800):
        """
        Render the knowledge graph in Streamlit.

        Args:
            html_path: Path to HTML file
            height: Height of iframe
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        components.html(html_content, height=height, scrolling=True)

    def get_graph_stats(self, G: nx.Graph) -> Dict:
        """
        Calculate graph statistics.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary with statistics
        """
        if len(G.nodes()) == 0:
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'isolated_nodes': 0,
                'avg_degree': 0,
                'density': 0,
                'connected_components': 0
            }

        isolated = list(nx.isolates(G))
        degrees = [deg for node, deg in G.degree()]

        return {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'isolated_nodes': len(isolated),
            'avg_degree': sum(degrees) / len(degrees) if degrees else 0,
            'density': nx.density(G),
            'connected_components': nx.number_connected_components(G)
        }

    def get_central_notes(self, G: nx.Graph, top_k: int = 5) -> List[Dict]:
        """
        Find the most central/connected notes.

        Args:
            G: NetworkX graph
            top_k: Number of top notes to return

        Returns:
            List of central notes with scores
        """
        if len(G.nodes()) == 0:
            return []

        # Calculate centrality
        centrality = nx.degree_centrality(G)

        # Sort by centrality
        sorted_nodes = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        # Get node details
        central_notes = []
        for node_id, score in sorted_nodes:
            data = G.nodes[node_id]
            central_notes.append({
                'id': node_id,
                'title': data.get('title', 'Untitled'),
                'tags': data.get('tags', []),
                'centrality_score': score,
                'connections': G.degree(node_id)
            })

        return central_notes

    def find_communities(self, G: nx.Graph) -> Dict:
        """
        Detect communities/clusters in the graph.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary mapping community ID to list of nodes
        """
        if len(G.nodes()) == 0:
            return {}

        # Use greedy modularity for community detection
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(G)

        community_dict = {}
        for i, comm in enumerate(communities):
            community_dict[i] = {
                'nodes': list(comm),
                'size': len(comm),
                'titles': [G.nodes[node]['title'] for node in comm]
            }

        return community_dict
