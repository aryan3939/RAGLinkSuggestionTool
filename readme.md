# 🔗 Internal Link Suggestion Tool

An AI-powered tool that automatically suggests the most relevant internal blog posts to link from any given blog post, complete with AI-generated reasons and anchor text suggestions.

**🚀 Live Demo**: https://raglinksuggestiontool.streamlit.app/

## 📋 Overview

This tool helps optimize internal linking for SEO by:

- Scraping all blog posts from your sitemap
- Generating semantic embeddings using Google AI
- Finding the most relevant posts using vector similarity search
- Using GPT-4o to generate linking reasons and natural anchor text

## ✨ Features

- **Automated Sitemap Scraping**: Fetches all blog posts from your XML sitemap
- **Semantic Search**: Uses Google's text-embedding-004 model for deep content understanding
- **AI-Powered Recommendations**: GPT-4o generates contextual reasons and anchor text
- **Simple UI**: Streamlit-based interface - no coding required
- **JSON Export**: Download results in the required format
- **Efficient Scraping**: Async scraping with Crawl4AI for JavaScript-rendered content
- **Persistent Database**: ChromaDB vector storage for fast repeated queries
- **Free Deployment**: Hosted on Streamlit Cloud

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for GPT-4o)
- Google AI API key (for embeddings)

### Installation

1. **Clone the repository**

   ```bash
   git clone <https://github.com/aryan3939/RAGLinkSuggestionTool>
   cd LinkSuggestionTool
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   playwright install  # Install browser for Crawl4AI
   ```

4. **Configure API keys**

   Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   Get your API keys:

   - OpenAI: https://platform.openai.com/api-keys
   - Google AI: https://aistudio.google.com/app/apikey

### Build the Database

**First-time setup** - This scrapes all posts and builds the vector database:

```bash
python build_database.py
```

This will:

1. Fetch all URLs from your sitemap
2. Scrape each blog post's content
3. Generate embeddings using Google AI
4. Store in ChromaDB for fast retrieval

⏱️ **Time estimate**: 5-10 minutes for 100 posts

### Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter a blog post URL** from your site
2. **Click "Find Similar Posts"**
3. **Review suggestions** with:
   - Similarity scores
   - AI-generated linking reasons
   - Suggested anchor text
4. **Download results** as JSON

### Example Output

```json
[
  {
    "from_post": "https://prostructengineering.com/example-post",
    "to_post": "https://prostructengineering.com/related-post",
    "reason": "Both posts discuss structural analysis methods and would provide readers with complementary technical insights on engineering calculations.",
    "anchor_text": "structural analysis techniques",
    "similarity_score": "87.5%"
  }
]
```

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting                    | Default                                   | Description                              |
| -------------------------- | ----------------------------------------- | ---------------------------------------- |
| `SITEMAP_URL`              | prostructengineering.com/post-sitemap.xml | Your blog's sitemap                      |
| `FINAL_SUGGESTIONS`        | 5                                         | Number of suggestions to show            |
| `USE_GOOGLE_EMBEDDINGS`    | True                                      | Use Google AI (cheaper) vs OpenAI        |
| `LLM_MODEL`                | gpt-4o                                    | Model for generating reasons/anchor text |
| `MAX_CONCURRENT_REQUESTS`  | 5                                         | Concurrent scraping threads              |
| `MIN_SIMILARITY_THRESHOLD` | 0.5                                       | Minimum similarity score (0-1)           |

## 📁 Project Structure

```
LinkSuggestionTool/
├── app.py                 # Streamlit UI application
├── build_database.py      # Database builder script
├── config.py              # Central configuration
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
├── utils/
│   ├── scraper.py         # Sitemap + content scraper
│   ├── embeddings.py      # Embedding generation & ChromaDB
│   ├── similarity.py      # Vector similarity search
│   └── llm_processor.py   # GPT-4o reason/anchor generation
└── data/
    └── chroma_db/         # Vector database (auto-created)
```

## 🔧 How It Works

### 1. **Scraping Phase** ([`utils/scraper.py`](utils/scraper.py))

- Fetches sitemap XML
- Scrapes each post using Crawl4AI (handles JavaScript)
- Extracts title + main content as markdown

### 2. **Embedding Phase** ([`utils/embeddings.py`](utils/embeddings.py))

- Converts content to 768-dim vectors using Google AI
- Stores in ChromaDB with COSINE similarity metric
- Persists to disk for reuse

### 3. **Search Phase** ([`utils/similarity.py`](utils/similarity.py))

- Accepts user's blog post URL
- Retrieves its embedding vector
- Finds top-K most similar posts via cosine similarity

### 4. **Enhancement Phase** ([`utils/llm_processor.py`](utils/llm_processor.py))

- Sends post pairs to GPT-4o
- Generates contextual linking reason
- Creates natural anchor text (3-7 words)

### 5. **Display Phase** ([`app.py`](app.py))

- Shows ranked results in Streamlit UI
- Provides JSON download

## 🛠️ Troubleshooting

### Database Not Found

**Solution**: Run `python build_database.py` first

### Scraping Fails

- Check internet connection
- Verify sitemap URL in `config.py`
- Try reducing `MAX_CONCURRENT_REQUESTS` to 2-3

### Out of Memory

- Reduce `MAX_CONCURRENT_REQUESTS` in `config.py`
- The tool monitors memory usage automatically

### API Rate Limits

- Google AI: 1500 requests/day (free tier)
- OpenAI: Based on your plan
- Solution: Reduce batch size or upgrade plan

### Playwright Browser Issues

```bash
playwright install chromium  # Reinstall browser
```

## 🔄 Updating the Database

To refresh with new blog posts:

```bash
python build_database.py
```

This will rebuild the entire database with latest content.

## 🧪 Tech Stack

- **Scraping**: Crawl4AI, BeautifulSoup4, Playwright
- **Embeddings**: LangChain, Google Generative AI
- **Vector DB**: ChromaDB (local, no server needed)
- **LLM**: OpenAI GPT-4o via LangChain
- **UI**: Streamlit
- **Async**: asyncio for concurrent scraping

## 📝 Requirements

See `requirements.txt` for full dependency list.
