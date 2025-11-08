"""ChromaDB vector store for semantic search."""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings

from ..utils.config import CHROMA_DB_PATH, ensure_directories


class VectorStore:
    """Manages vector embeddings in ChromaDB."""

    def __init__(self, collection_name: str = "notes", persist_directory: Optional[str] = None):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the Chroma collection
            persist_directory: Directory to persist the database
        """
        if persist_directory is None:
            ensure_directories()
            persist_directory = str(CHROMA_DB_PATH)

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Personal notes knowledge base"}
        )

        self.collection_name = collection_name

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> bool:
        """
        Add documents with their embeddings to the vector store.

        Args:
            ids: List of document IDs
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas if metadatas else None
            )
            return True
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False

    def add_document(
        self,
        doc_id: str,
        embedding: List[float],
        document: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add a single document to the vector store.

        Args:
            doc_id: Document ID
            embedding: Embedding vector
            document: Document text
            metadata: Optional metadata dictionary

        Returns:
            True if successful, False otherwise
        """
        return self.add_documents(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata] if metadata else None
        )

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store for similar documents.

        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            where: Optional filter conditions

        Returns:
            Dictionary containing results
        """
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "distances": []}

    def query_single(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query with a single embedding vector.

        Args:
            query_embedding: Single query embedding vector
            n_results: Number of results to return
            where: Optional filter conditions

        Returns:
            Dictionary containing results
        """
        results = self.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        # Unwrap the single query results
        if results and results['ids']:
            return {
                'ids': results['ids'][0],
                'documents': results['documents'][0],
                'metadatas': results['metadatas'][0],
                'distances': results['distances'][0]
            }
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Personal notes knowledge base"}
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

    def count(self) -> int:
        """
        Get the number of documents in the collection.

        Returns:
            Number of documents
        """
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0
