"""
Link Suggestion Tool - Streamlit App
Simple UI for finding internal linking opportunities.
"""

import streamlit as st
from utils.embeddings import initialize_database
from utils.similarity import create_searcher
from utils.llm_processor import create_llm_processor


# Page config
st.set_page_config(
    page_title="Internal Link Suggestion Tool",
    page_icon="🔗",
    layout="wide"
)

# Title
st.title("🔗 Internal Link Suggestion Tool")
st.markdown("Find the most relevant internal blog posts to link from your content.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup")
    
    st.markdown("### First Time Setup")
    st.info("Before using this app, build the database:")
    st.code("python build_database.py", language="bash")
    
    st.markdown("---")
    
    st.markdown("### Instructions")
    st.markdown("1. Build database (see above)")
    st.markdown("2. Enter a blog post URL below")
    st.markdown("3. Click 'Find Similar Posts'")
    st.markdown("4. Download results as JSON")

# Main area
st.markdown("---")

# Try to load database
try:
    if 'manager' not in st.session_state:
        with st.spinner("Loading database..."):
            manager = initialize_database()
            st.session_state['manager'] = manager
            st.success("✅ Database loaded successfully!")
    else:
        manager = st.session_state['manager']
        
except Exception as e:
    st.error("⚠️ Database not found!")
    st.warning("Please build the database first by running:")
    st.code("python build_database.py", language="bash")
    st.info("💡 This needs to be run in your terminal (not in Streamlit)")
    st.stop()

# Input section
st.subheader("📝 Enter Blog Post URL")

# Create searcher and LLM processor
searcher = create_searcher(manager)
llm_processor = create_llm_processor()

# Get all available URLs
all_urls = searcher.get_all_urls()

if all_urls:
    st.caption(f"Database contains {len(all_urls)} blog posts")

# URL input
url_input = st.text_input(
    "Blog Post URL:",
    placeholder="https://prostructengineering.com/your-blog-post",
    help="Enter the URL of the blog post you want to find internal links for"
)

# Search button
if st.button("🔍 Find Similar Posts", type="primary"):
    if not url_input:
        st.error("⚠️ Please enter a URL")
    elif url_input not in all_urls:
        st.error("❌ URL not found in database")
        st.info("💡 Make sure the URL is from your sitemap and the database is up to date")
        
        with st.expander("Show available URLs (first 10)"):
            for url in all_urls[:10]:
                st.text(url)
            if len(all_urls) > 10:
                st.caption(f"...and {len(all_urls) - 10} more")
    else:
        # Show spinner while processing
        with st.spinner("🔍 Searching for similar posts..."):
            similar_posts = searcher.find_similar_posts(url_input)
            
            if not similar_posts:
                st.warning("No similar posts found above the similarity threshold.")
                st.info(f"💡 Try lowering MIN_SIMILARITY_THRESHOLD in config.py (currently {manager.vectorstore._collection.metadata})")
            else:
                # Get target post info
                target_context = searcher.get_post_context(url_input)
                target_title = None
                for metadata in manager.vectorstore.get()['metadatas']:
                    if metadata.get('url') == url_input:
                        target_title = metadata.get('title')
                        break
                
                target_post = {
                    'title': target_title or url_input,
                    'content': target_context or ''
                }
                
                # Generate reasons and anchor text
                with st.spinner("🤖 Generating reasons and anchor text with GPT-4o..."):
                    enhanced_results = llm_processor.process_all_suggestions(
                        target_post,
                        similar_posts
                    )
                
                # Display results
                st.success(f"✅ Found {len(enhanced_results)} similar posts")
                st.markdown("---")
                
                # Show results
                for i, result in enumerate(enhanced_results, 1):
                    with st.expander(f"#{i} - {result['title']}", expanded=(i==1)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**URL:** [{result['url']}]({result['url']})")
                            st.markdown(f"**Similarity Score:** {result['similarity']:.2%}")
                        
                        with col2:
                            st.metric("Rank", f"#{i}")
                        
                        st.markdown("**Why Link These Posts:**")
                        st.info(result['reason'])
                        
                        st.markdown("**Suggested Anchor Text:**")
                        st.code(result['anchor_text'], language=None)
                
                # Download results as JSON
                st.markdown("---")
                import json
                
                download_data = [{
                    "from_post": url_input,
                    "to_post": r['url'],
                    "reason": r['reason'],
                    "anchor_text": r['anchor_text'],
                    "similarity_score": f"{r['similarity']:.2%}"
                } for r in enhanced_results]
                
                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=json.dumps(download_data, indent=2),
                    file_name="link_suggestions.json",
                    mime="application/json"
                )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Built with Streamlit • Powered by OpenAI & Crawl4AI"
    "</div>",
    unsafe_allow_html=True
)
