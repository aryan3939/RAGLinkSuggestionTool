"""
Embeddings module for generating and storing blog post embeddings using OpenAI and ChromaDB.
"""

import os
from typing import List, Dict, Optional
from tqdm import tqdm

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config import Config


class EmbeddingsManager:
    """Manages embedding generation and vector database operations."""
    
    def __init__(self):
        """Initialize embeddings manager with Google AI or OpenAI and ChromaDB."""
        
        # Initialize embeddings based on config
        if Config.USE_GOOGLE_EMBEDDINGS:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                google_api_key=Config.GOOGLE_API_KEY
            )
            provider = "Google AI Studio"
        else:
            self.embeddings = OpenAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY
            )
            provider = "OpenAI"
        
        # Ensure data directory exists
        os.makedirs(Config.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Initialize or load existing ChromaDB
        self.vectorstore = None
        
        print("✅ Embeddings manager initialized")
        print(f"   Provider: {provider}")
        print(f"   Model: {Config.EMBEDDING_MODEL}")
        print(f"   Storage: {Config.CHROMA_PERSIST_DIR}")
    
    
    def create_documents(self, posts: List[Dict[str, str]]) -> List[Document]:
        """
        Convert scraped posts to LangChain Document objects.
        
        Args:
            posts: List of dicts with 'url', 'title', 'content'
            
        Returns:
            List of Document objects ready for embedding
        """
        documents = []
        
        for post in posts:
            # Combine title and content for embedding
            text = f"{post['title']}\n\n{post['content']}"
            
            # Create Document with metadata
            doc = Document(
                page_content=text,
                metadata={
                    'url': post['url'],
                    'title': post['title'],
                    'source': 'blog_post'
                }
            )
            documents.append(doc)
        
        print(f"📄 Created {len(documents)} documents")
        return documents
    
    def build_vectorstore(self, posts: List[Dict[str, str]], show_progress: bool = True) -> Chroma:
        """
        Build vector database from blog posts using COSINE similarity.
        
        Args:
            posts: List of scraped blog posts
            show_progress: Show progress bar during embedding
            
        Returns:
            ChromaDB vectorstore instance
        """
        print(f"\n🔮 Building vector database...")
        print(f"   Posts to embed: {len(posts)}")
        print(f"   Distance metric: COSINE (best for text embeddings)")
        
        # Convert to documents
        documents = self.create_documents(posts)
        
        # Generate embeddings and store in ChromaDB
        print("   Generating embeddings (this may take a few minutes)...")
        
        if show_progress:
            # Process with progress bar
            batch_size = 10
            
            with tqdm(total=len(documents), desc="Embedding posts") as pbar:
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    
                    if self.vectorstore is None:
                        # Create new vectorstore with COSINE metric
                        self.vectorstore = Chroma.from_documents(
                            documents=batch,
                            embedding=self.embeddings,
                            persist_directory=Config.CHROMA_PERSIST_DIR,
                            collection_name=Config.COLLECTION_NAME,
                            collection_metadata={"hnsw:space": "cosine"}  # ⬅️ FIX: Use cosine!
                        )
                    else:
                        # Add to existing vectorstore
                        self.vectorstore.add_documents(batch)
                    
                    pbar.update(len(batch))
        else:
            # Process all at once
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=Config.CHROMA_PERSIST_DIR,
                collection_name=Config.COLLECTION_NAME,
                collection_metadata={"hnsw:space": "cosine"}  # ⬅️ FIX: Use cosine!
            )
        
        print(f"✅ Vector database built with {len(documents)} posts")
        return self.vectorstore


    def load_vectorstore(self) -> Optional[Chroma]:
        """
        Load existing vector database from disk with COSINE metric.
        
        Returns:
            ChromaDB vectorstore or None if doesn't exist
        """
        try:
            self.vectorstore = Chroma(
                persist_directory=Config.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
                collection_name=Config.COLLECTION_NAME,
                collection_metadata={"hnsw:space": "cosine"}  # ⬅️ FIX: Use cosine!
            )
            
            # Check if vectorstore has documents
            count = self.vectorstore._collection.count()
            
            if count > 0:
                print(f"✅ Loaded existing vector database ({count} posts)")
                print(f"   Distance metric: COSINE")
                return self.vectorstore
            else:
                print("⚠️ Vector database exists but is empty")
                return None
                
        except Exception as e:
            print(f"⚠️ No existing vector database found: {e}")
            return None

    
    def get_or_create_vectorstore(self, posts: List[Dict[str, str]] = None) -> Chroma:
        """
        Load existing vectorstore or create new one if doesn't exist.
        
        Args:
            posts: Blog posts to use if creating new vectorstore
            
        Returns:
            ChromaDB vectorstore
        """
        # Try loading existing
        existing = self.load_vectorstore()
        
        if existing:
            return existing
        
        # Create new if posts provided
        if posts:
            print("📦 Creating new vector database...")
            return self.build_vectorstore(posts)
        
        raise ValueError("No existing vectorstore found and no posts provided to create one")
    
    
    def add_posts(self, new_posts: List[Dict[str, str]]):
        """
        Add new blog posts to existing vector database.
        
        Args:
            new_posts: List of new posts to add
        """
        if not self.vectorstore:
            print("⚠️ No vectorstore loaded. Creating new one...")
            self.build_vectorstore(new_posts)
            return
        
        print(f"\n➕ Adding {len(new_posts)} new posts to vector database...")
        
        documents = self.create_documents(new_posts)
        self.vectorstore.add_documents(documents)
        
        print(f"✅ Added {len(new_posts)} posts to database")
    
    
    def search_similar(self, query_url: str, k: int = None) -> List[Dict]:
        """
        Find similar blog posts using COSINE similarity.
        
        Args:
            query_url: URL of the blog post to find similar posts for
            k: Number of similar posts to return
            
        Returns:
            List of similar posts with metadata and similarity scores
        """
        if k is None:
            k = Config.TOP_K_RESULTS
        
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Load or create one first.")
        
        # Get all documents to find the query post
        all_docs = self.vectorstore.get()
        
        # Find the query post
        query_doc = None
        for i, url in enumerate(all_docs['metadatas']):
            if url.get('url') == query_url:
                query_doc = all_docs['documents'][i]
                break
        
        if not query_doc:
            raise ValueError(f"URL not found in database: {query_url}")
        
        # Search for similar documents
        results = self.vectorstore.similarity_search_with_score(
            query_doc,
            k=k + 1  # +1 because query post will be in results
        )
        
        # Filter out the query post itself and format results
        similar_posts = []
        for doc, score in results:
            # Skip if it's the query post itself
            if doc.metadata.get('url') == query_url:
                continue
            
            # With COSINE: score is already cosine distance (0 = identical, 2 = opposite)
            # Convert to similarity: similarity = 1 - (distance / 2)
            # This gives us a 0-1 scale where 1 = identical
            similarity = 1 - (score / 2)
            
            # Apply threshold
            if similarity >= Config.MIN_SIMILARITY_THRESHOLD:
                similar_posts.append({
                    'url': doc.metadata.get('url'),
                    'title': doc.metadata.get('title'),
                    'content': doc.page_content,
                    'similarity': similarity
                })
        
        # Sort by similarity (highest first) and limit to k results
        similar_posts.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_posts[:k]



def initialize_database(posts: List[Dict[str, str]] = None, force_rebuild: bool = False) -> EmbeddingsManager:
    """
    Initialize or load the embeddings database.
    
    Args:
        posts: Blog posts to use if creating new database
        force_rebuild: If True, rebuild database even if it exists
        
    Returns:
        Initialized EmbeddingsManager
    """
    manager = EmbeddingsManager()
    
    if force_rebuild and posts:
        print("🔄 Force rebuild requested...")
        manager.build_vectorstore(posts)
    else:
        manager.get_or_create_vectorstore(posts)
    
    return manager
