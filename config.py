import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration class for the Link Suggestion Tool.
    All settings and constants are defined here.
    """
    
    # API Configuration
    # Try Streamlit secrets first, fallback to environment variables
    try:
        import streamlit as st
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
    except:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Embedding Provider Selection
    USE_GOOGLE_EMBEDDINGS = True  # Set to False to use OpenAI embeddings
    
    # Model Settings
    EMBEDDING_MODEL = "models/text-embedding-004" if USE_GOOGLE_EMBEDDINGS else "text-embedding-3-small"
    LLM_MODEL = "gpt-4o"  # Most capable model for generating reasons and anchor text
    
    # Sitemap URL
    SITEMAP_URL = "https://prostructengineering.com/post-sitemap.xml"
    
    # Vector Database Settings
    CHROMA_PERSIST_DIR = "data/chroma_db"  # Where to save the vector database
    COLLECTION_NAME = "blog_posts"  # Name of the collection in ChromaDB
    
    # Similarity Search Settings
    TOP_K_RESULTS = 10  # How many similar posts to retrieve initially
    FINAL_SUGGESTIONS = 5  # Show exactly 5 suggestions to the user
    MIN_SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score (0-1 scale)
    
    # Scraping Settings - Crawl4AI Configuration
    USE_CRAWL4AI = True  # Use Crawl4AI as primary scraper (fallback to BeautifulSoup if needed)
    REQUEST_TIMEOUT = 30  # Seconds to wait for web requests
    DELAY_BETWEEN_REQUESTS = 1  # Seconds to wait between scraping (be polite to servers)
    MAX_CONCURRENT_REQUESTS = 5  # How many pages to scrape at once (async)
    
    # Crawl4AI Specific Settings
    CRAWL4AI_VERBOSE = False  # Set to True for debugging
    CRAWL4AI_HEADLESS = True  # Run browser in headless mode (no UI)
    CRAWL4AI_BROWSER_TYPE = "chromium"  # Options: chromium, firefox, webkit
    
    # Content Extraction Settings
    MAX_CONTENT_LENGTH = 10000  # Maximum characters to extract from each post
    EXTRACT_IMAGES = False  # Don't extract images (we only need text)
    EXTRACT_LINKS = False  # Don't need internal links during extraction
    
    # Content Cleaning
    REMOVE_NAVIGATION = True  # Remove nav menus, headers, footers
    REMOVE_SIDEBAR = True  # Remove sidebar content
    REMOVE_ADS = True  # Remove advertisement sections
    
    # LLM Prompt Templates
    REASON_PROMPT_TEMPLATE = """
You are an SEO expert analyzing blog post relationships for internal linking.

Target Post Title: {target_title}
Target Post Excerpt: {target_excerpt}

Similar Post Title: {similar_title}
Similar Post Excerpt: {similar_excerpt}

Write ONE concise sentence explaining why these posts should be linked together.
Focus on the semantic relationship, topical overlap, and value to the reader.
Keep it professional and informative.
"""
    
    ANCHOR_TEXT_PROMPT_TEMPLATE = """
You are a content strategist creating natural anchor text for internal blog links.

Context from Target Post: {target_context}
Post to Link To: {similar_title}

Generate a natural, contextual anchor text phrase (3-7 words) for linking to the similar post.

Requirements:
- Must sound natural in a sentence
- Should be descriptive and keyword-rich
- Must relate to the similar post's topic
- Avoid generic phrases like "click here", "read more", "this article"

Return ONLY the anchor text phrase, nothing else.
"""

    # Cache Settings
    CACHE_EMBEDDINGS = True  # Store embeddings to avoid regenerating
    CACHE_SCRAPED_CONTENT = True  # Store scraped content locally
    CACHE_EXPIRY_DAYS = 7  # Refresh cached content after 7 days
    
    # Error Handling
    MAX_RETRIES = 3  # How many times to retry failed requests
    RETRY_DELAY = 2  # Seconds to wait between retries
    SKIP_ON_ERROR = True  # Continue scraping even if some pages fail

# Validate that required API keys exist
if Config.USE_GOOGLE_EMBEDDINGS:
    if not Config.GOOGLE_API_KEY:
        raise ValueError(
            "⚠️ Google API key not found! Please add GOOGLE_API_KEY to your .env file\n"
            "Get your API key from: https://aistudio.google.com/app/apikey"
        )
else:
    if not Config.OPENAI_API_KEY:
        raise ValueError(
            "⚠️ OpenAI API key not found! Please add OPENAI_API_KEY to your .env file\n"
            "Get your API key from: https://platform.openai.com/api-keys"
        )

print("✅ Configuration loaded successfully!")
print(f"🔮 Embeddings: {'Google AI Studio' if Config.USE_GOOGLE_EMBEDDINGS else 'OpenAI'}")
print(f"📊 Using model: {Config.LLM_MODEL}")
print(f"🔍 Will show {Config.FINAL_SUGGESTIONS} suggestions per query")
print(f"🕷️ Scraper: {'Crawl4AI (AI-optimized)' if Config.USE_CRAWL4AI else 'BeautifulSoup (Traditional)'}")
