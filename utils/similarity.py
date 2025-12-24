"""
Similarity search module for finding related blog posts.
Coordinates embeddings search and result preparation.
"""

from typing import List, Dict, Optional
from utils.embeddings import EmbeddingsManager
from config import Config


class SimilaritySearcher:
    """Handles similarity search operations and result formatting."""
    
    def __init__(self, embeddings_manager: EmbeddingsManager):
        """
        Initialize similarity searcher.
        
        Args:
            embeddings_manager: Initialized embeddings manager with loaded vectorstore
        """
        self.embeddings_manager = embeddings_manager
        print("🔍 Similarity searcher initialized")
    
    
    def find_similar_posts(self, query_url: str, top_k: int = None) -> List[Dict]:
        """
        Find similar blog posts for a given URL.
        
        Args:
            query_url: URL of the blog post to find similar posts for
            top_k: Number of results to return (uses config default if None)
            
        Returns:
            List of similar posts with metadata and scores
        """
        if top_k is None:
            top_k = Config.FINAL_SUGGESTIONS
        
        print(f"\n🔍 Searching for similar posts to:")
        print(f"   {query_url}")
        
        try:
            # Search using embeddings manager
            results = self.embeddings_manager.search_similar(
                query_url=query_url,
                k=top_k
            )
            
            if not results:
                print("⚠️ No similar posts found above similarity threshold")
                return []
            
            print(f"✅ Found {len(results)} similar posts")
            
            # Add ranking
            for i, result in enumerate(results, 1):
                result['rank'] = i
            
            return results
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error during search: {e}")
            return []
    
    
    def get_post_context(self, url: str, max_chars: int = 500) -> Optional[str]:
        """
        Get context snippet from a blog post for LLM processing.
        
        Args:
            url: URL of the post
            max_chars: Maximum characters to return
            
        Returns:
            Text snippet from the post
        """
        try:
            # Get the document from vectorstore
            all_docs = self.embeddings_manager.vectorstore.get()
            
            for i, metadata in enumerate(all_docs['metadatas']):
                if metadata.get('url') == url:
                    content = all_docs['documents'][i]
                    # Return first max_chars characters
                    return content[:max_chars] + "..." if len(content) > max_chars else content
            
            return None
            
        except Exception as e:
            print(f"⚠️ Could not get context for {url}: {e}")
            return None
    
    
    def validate_url(self, url: str) -> bool:
        """
        Check if a URL exists in the vector database.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL exists in database
        """
        try:
            all_docs = self.embeddings_manager.vectorstore.get()
            
            for metadata in all_docs['metadatas']:
                if metadata.get('url') == url:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error validating URL: {e}")
            return False
    
    
    def get_all_urls(self) -> List[str]:
        """
        Get all URLs stored in the vector database.
        
        Returns:
            List of all blog post URLs
        """
        try:
            all_docs = self.embeddings_manager.vectorstore.get()
            urls = [metadata.get('url') for metadata in all_docs['metadatas']]
            return [url for url in urls if url]  # Filter out None values
            
        except Exception as e:
            print(f"⚠️ Error getting URLs: {e}")
            return []


def create_searcher(embeddings_manager: EmbeddingsManager) -> SimilaritySearcher:
    """
    Factory function to create a similarity searcher.
    
    Args:
        embeddings_manager: Initialized embeddings manager
        
    Returns:
        SimilaritySearcher instance
    """
    return SimilaritySearcher(embeddings_manager)
