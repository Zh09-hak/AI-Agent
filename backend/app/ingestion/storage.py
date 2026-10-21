import chromadb
from chromadb.config import Settings
from pathlib import Path


class VectorStore:
    def __init__(self, persist_directory: str = "data/vector_store"):
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Company document chunks and embeddings"}
        )
    
    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]]
    ) -> int:

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])
            metadata = {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "total_chunks": chunk["total_chunks"],
            }
            
            if chunk.get("page_number") is not None:
                metadata["page_number"] = chunk["page_number"]
            
            metadatas.append(metadata)
        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        
        return len(ids)
    
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                search_results.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })
        
        return search_results
    
    def delete_by_document_id(self, document_id: str) -> int:
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            return len(results["ids"])
        
        return 0
    
    def get_document_chunks(self, document_id: str) -> list[dict]:
        results = self.collection.get(
            where={"document_id": document_id},
            include=["documents", "metadatas"]
        )
        
        chunks = []
        if results["ids"]:
            for i, chunk_id in enumerate(results["ids"]):
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                })
        
        return chunks
    
    def count_chunks(self) -> int:
        return self.collection.count()

vector_store = VectorStore()