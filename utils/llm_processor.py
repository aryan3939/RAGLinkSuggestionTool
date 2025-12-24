"""
LLM processor for generating link reasons and anchor text using GPT-4o.
"""

from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import Config


class LLMProcessor:
    """Generates reasons and anchor text for internal links using GPT-4o."""
    
    def __init__(self):
        """Initialize LLM processor with GPT-4o."""
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=0.7,  # Balanced creativity
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Create prompt templates
        self.reason_prompt = PromptTemplate.from_template(Config.REASON_PROMPT_TEMPLATE)
        self.anchor_prompt = PromptTemplate.from_template(Config.ANCHOR_TEXT_PROMPT_TEMPLATE)
        print("🤖 LLM Processor initialized")
        print(f"   Model: {Config.LLM_MODEL}")
    
    
    def generate_reason(self, target_title: str, target_excerpt: str, 
                       similar_title: str, similar_excerpt: str) -> str:
        """
        Generate a reason for why two posts should be linked.
        
        Args:
            target_title: Title of the main post
            target_excerpt: Excerpt from the main post
            similar_title: Title of the similar post
            similar_excerpt: Excerpt from the similar post
            
        Returns:
            One-sentence explanation of why posts should be linked
        """
        try:
            # Format the prompt
            formatted_prompt = self.reason_prompt.format(
                target_title=target_title,
                target_excerpt=target_excerpt,
                similar_title=similar_title,
                similar_excerpt=similar_excerpt
            )
            
            # Get response from GPT-4o
            response = self.llm.invoke(formatted_prompt)
            reason = response.content.strip()
            
            return reason
            
        except Exception as e:
            print(f"⚠️ Error generating reason: {e}")
            return "These posts cover related topics and would benefit from internal linking."
    
    
    def generate_anchor_text(self, target_context: str, similar_title: str) -> str:
        """
        Generate natural anchor text for linking.
        
        Args:
            target_context: Context from the target post
            similar_title: Title of the post to link to
            
        Returns:
            Natural anchor text phrase (3-7 words)
        """
        try:
            # Format the prompt
            formatted_prompt = self.anchor_prompt.format(
                target_context=target_context,
                similar_title=similar_title
            )
            
            # Get response from GPT-4o
            response = self.llm.invoke(formatted_prompt)
            anchor_text = response.content.strip()
            
            # Clean up quotes if present
            anchor_text = anchor_text.strip('"').strip("'")
            
            return anchor_text
            
        except Exception as e:
            print(f"⚠️ Error generating anchor text: {e}")
            # Fallback to simple anchor text
            return similar_title
    
    
    def process_similar_post(self, target_post: Dict, similar_post: Dict) -> Dict:
        """
        Process a similar post to generate reason and anchor text.
        
        Args:
            target_post: Dict with 'title' and 'content'
            similar_post: Dict with 'title', 'content', 'url', 'similarity'
            
        Returns:
            Enhanced dict with 'reason' and 'anchor_text' added
        """
        # Get excerpts (first 300 chars)
        target_excerpt = target_post.get('content', '')[:300]
        similar_excerpt = similar_post.get('content', '')[:300]
        
        # Generate reason
        reason = self.generate_reason(
            target_title=target_post.get('title', ''),
            target_excerpt=target_excerpt,
            similar_title=similar_post.get('title', ''),
            similar_excerpt=similar_excerpt
        )
        
        # Generate anchor text
        anchor_text = self.generate_anchor_text(
            target_context=target_excerpt,
            similar_title=similar_post.get('title', '')
        )
        
        # Add to result
        result = similar_post.copy()
        result['reason'] = reason
        result['anchor_text'] = anchor_text
        
        return result
    
    
    def process_all_suggestions(self, target_post: Dict, similar_posts: List[Dict]) -> List[Dict]:
        """
        Process all similar posts to add reasons and anchor text.
        
        Args:
            target_post: The main blog post
            similar_posts: List of similar posts from similarity search
            
        Returns:
            Enhanced list with reasons and anchor text for each suggestion
        """
        print(f"\n🤖 Generating reasons and anchor text for {len(similar_posts)} suggestions...")
        
        enhanced_results = []
        
        for i, similar_post in enumerate(similar_posts, 1):
            print(f"   Processing {i}/{len(similar_posts)}: {similar_post.get('title', 'Unknown')[:50]}...")
            
            enhanced = self.process_similar_post(target_post, similar_post)
            enhanced_results.append(enhanced)
        
        print("✅ All suggestions processed")
        return enhanced_results


def create_llm_processor() -> LLMProcessor:
    """
    Factory function to create an LLM processor.
    
    Returns:
        LLMProcessor instance
    """
    return LLMProcessor()
