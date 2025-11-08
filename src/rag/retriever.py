"""Retrieve relevant notes based on semantic search."""
from typing import List, Dict, Optional

from ..db.vectorstore import VectorStore
from ..db.metadata import MetadataDB
from ..utils.file_loader import load_all_notes, get_note_by_id
from .embedder import Embedder
from ..utils.config import TOP_K_RESULTS


class Retriever:
    """Handles retrieval of relevant notes."""

    def __init__(self):
        """Initialize the retriever with necessary components."""
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.metadata_db = MetadataDB()

    def index_all_notes(self) -> int:
        """
        Index all notes from the notes directory.

        Returns:
            Number of notes indexed
        """
        print("Loading notes from directory...")
        notes = load_all_notes()

        if not notes:
            print("No notes found to index.")
            return 0

        print(f"Found {len(notes)} notes. Indexing...")

        # Store metadata in SQLite
        count = self.metadata_db.insert_notes(notes)
        print(f"Stored metadata for {count} notes in SQLite.")

        # Generate embeddings and store in Chroma
        ids = [note['id'] for note in notes]
        documents = [note['content'] for note in notes]
        metadatas = [
            {
                'title': note['title'],
                'path': note['path'],
                'tags': note['tags']
            }
            for note in notes
        ]

        print("Generating embeddings...")
        embeddings = self.embedder.embed_texts(documents)

        print("Storing embeddings in vector store...")
        self.vector_store.add_documents(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Successfully indexed {len(notes)} notes.")
        return len(notes)

    def search_semantic(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Perform semantic search for relevant notes.

        Args:
            query: The search query
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing note information and relevance scores
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)

        # Search vector store
        results = self.vector_store.query_single(
            query_embedding=query_embedding,
            n_results=top_k
        )

        # Format results
        formatted_results = []
        for i, doc_id in enumerate(results['ids']):
            # Get full metadata from SQLite
            note_metadata = self.metadata_db.get_note_by_id(doc_id)

            result = {
                'id': doc_id,
                'title': results['metadatas'][i].get('title', 'Untitled'),
                'content': results['documents'][i],
                'path': results['metadatas'][i].get('path', ''),
                'tags': results['metadatas'][i].get('tags', ''),
                'distance': results['distances'][i],
                'relevance_score': 1 - results['distances'][i]  # Convert distance to similarity
            }

            formatted_results.append(result)

        return formatted_results

    def search_keyword(self, keyword: str) -> List[Dict]:
        """
        Perform keyword search in note titles and tags.

        Args:
            keyword: The keyword to search for

        Returns:
            List of dictionaries containing note information
        """
        results = self.metadata_db.search_by_keyword(keyword)
        return results

    def search_hybrid(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword search.

        Args:
            query: The search query
            top_k: Number of top results to return

        Returns:
            List of dictionaries containing note information
        """
        # Get semantic search results
        semantic_results = self.search_semantic(query, top_k=top_k)

        # Get keyword search results
        keyword_results = self.search_keyword(query)

        # Combine results, prioritizing semantic search
        combined = {}

        # Add semantic results with their scores
        for result in semantic_results:
            combined[result['id']] = result

        # Add keyword results if not already present
        for result in keyword_results:
            if result['id'] not in combined:
                # Load full content for keyword results
                note = load_all_notes()
                note_data = next((n for n in note if n['id'] == result['id']), None)
                if note_data:
                    result['content'] = note_data['content']
                    result['relevance_score'] = 0.5  # Lower score for keyword-only matches
                    combined[result['id']] = result

        # Sort by relevance score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x.get('relevance_score', 0),
            reverse=True
        )

        return sorted_results[:top_k]

    def get_note_content(self, note_id: str) -> Optional[str]:
        """
        Get the full content of a note by its ID.

        Args:
            note_id: The note ID

        Returns:
            Note content or None if not found
        """
        note = get_note_by_id(note_id)
        return note['content'] if note else None

    def get_stats(self) -> Dict:
        """
        Get statistics about the indexed notes.

        Returns:
            Dictionary containing statistics
        """
        return {
            'total_notes': self.vector_store.count(),
            'notes_in_db': len(self.metadata_db.get_all_notes())
        }

    def close(self):
        """Close database connections."""
        self.metadata_db.close()
