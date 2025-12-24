"""
Build Database Script
Run this separately from Streamlit to build the vector database.
"""

from utils.scraper import scrape_all_posts
from utils.embeddings import initialize_database

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Link Suggestion Tool - Database Builder")
    print("="*60)
    
    # Step 1: Scrape posts
    print("\n📡 STEP 1: Scraping blog posts from sitemap...")
    print("-" * 60)
    
    posts = scrape_all_posts()
    
    if not posts:
        print("\n❌ ERROR: Failed to scrape posts")
        print("Please check your internet connection and sitemap URL")
        exit(1)
    
    print(f"\n✅ Successfully scraped {len(posts)} blog posts")
    
    # Step 2: Build vector database
    print("\n🔮 STEP 2: Building vector database...")
    print("-" * 60)
    print("⏳ This will take a few minutes...")
    
    try:
        manager = initialize_database(posts, force_rebuild=True)
        
        print("\n" + "="*60)
        print("✅ DATABASE BUILD COMPLETE!")
        print("="*60)
        print(f"\n📊 Statistics:")
        print(f"   - Total posts embedded: {len(posts)}")
        print(f"   - Database location: {manager.vectorstore._persist_directory}")
        print(f"   - Collection name: {manager.vectorstore._collection.name}")
        
        print(f"\n👉 Next step: Run the Streamlit app")
        print(f"   Command: streamlit run app.py")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR building database: {e}")
        exit(1)
