"""
Optimized blog scraper using Crawl4AI with browser reuse and memory monitoring.
Based on best practices from Crawl4AI documentation.
"""

import os
import asyncio
import psutil
from typing import List, Dict, Optional
from xml.etree import ElementTree

import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from config import Config


class BlogScraper:
    """Efficient blog scraper with browser reuse and memory tracking."""
    
    def __init__(self):
        self.sitemap_url = Config.SITEMAP_URL
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_content_length = Config.MAX_CONTENT_LENGTH
        self.max_concurrent = Config.MAX_CONCURRENT_REQUESTS
        
        # Memory tracking
        self.peak_memory = 0
        self.process = psutil.Process(os.getpid())
        
        print("🕷️ Scraper initialized with browser reuse optimization")
    
    
    def log_memory(self, prefix: str = ""):
        """Track and log memory usage."""
        current_mem = self.process.memory_info().rss  # in bytes
        if current_mem > self.peak_memory:
            self.peak_memory = current_mem
        
        current_mb = current_mem // (1024 * 1024)
        peak_mb = self.peak_memory // (1024 * 1024)
        print(f"{prefix} Memory: {current_mb} MB | Peak: {peak_mb} MB")
    
    
    def fetch_sitemap_urls(self) -> List[str]:
        """
        Fetch all blog post URLs from sitemap.
        
        Returns:
            List of blog post URLs
        """
        print(f"\n📡 Fetching sitemap: {self.sitemap_url}")
        
        try:
            response = requests.get(self.sitemap_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse XML
            root = ElementTree.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Extract URLs from <loc> tags
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace) if loc.text]
            
            print(f"✅ Found {len(urls)} blog posts")
            return urls
            
        except Exception as e:
            print(f"❌ Error fetching sitemap: {e}")
            return []
    
    
    async def scrape_all(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Scrape all blog posts with browser reuse and memory optimization.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraped blog posts
        """
        print(f"\n🚀 Starting optimized scrape of {len(urls)} posts")
        print(f"   Concurrency: {self.max_concurrent} posts at a time")
        
        # Configure browser with optimization flags
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        
        # Configure crawler to bypass cache for fresh content
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,  # Minimum words to extract
        )
        
        # Create single crawler instance (reused across all requests)
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.start()
        
        results = []
        success_count = 0
        fail_count = 0
        
        try:
            # Process URLs in batches
            for i in range(0, len(urls), self.max_concurrent):
                batch = urls[i:i + self.max_concurrent]
                batch_num = i // self.max_concurrent + 1
                total_batches = (len(urls) + self.max_concurrent - 1) // self.max_concurrent
                
                print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} posts)")
                
                # Log memory before batch
                self.log_memory(prefix="  Before:")
                
                # Create tasks with unique session IDs
                tasks = []
                for j, url in enumerate(batch):
                    session_id = f"blog_session_{i + j}"
                    task = crawler.arun(
                        url=url,
                        config=crawl_config,
                        session_id=session_id
                    )
                    tasks.append((url, task))
                
                # Execute batch concurrently
                batch_results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                # Log memory after batch
                self.log_memory(prefix="  After: ")
                
                # Process results
                for (url, _), result in zip(tasks, batch_results):
                    if isinstance(result, Exception):
                        print(f"   ❌ Error: {url[:60]}... - {result}")
                        fail_count += 1
                    elif result.success:
                        # Extract data
                        title = result.metadata.get('title', '').strip() or result.title or "Untitled"
                        content = result.markdown.strip()
                        
                        # Truncate if needed
                        if len(content) > self.max_content_length:
                            content = content[:self.max_content_length]
                        
                        results.append({
                            'url': url,
                            'title': title,
                            'content': content
                        })
                        success_count += 1
                        print(f"   ✅ {title[:60]}")
                    else:
                        print(f"   ⚠️ Failed: {url[:60]}...")
                        fail_count += 1
                
                print(f"   Batch success: {success_count}/{success_count + fail_count}")
                
                # Small delay between batches
                if i + self.max_concurrent < len(urls):
                    await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        finally:
            print("\n🔒 Closing crawler...")
            await crawler.close()
            self.log_memory(prefix="Final:")
            print(f"\n📊 Peak Memory: {self.peak_memory // (1024 * 1024)} MB")
        
        print(f"\n✅ Scraping complete:")
        print(f"   Success: {success_count}")
        print(f"   Failed: {fail_count}")
        print(f"   Total: {len(results)} posts extracted")
        
        return results


def scrape_all_posts() -> List[Dict[str, str]]:
    """
    Main function to scrape all blog posts from sitemap.
    
    Returns:
        List of scraped blog posts with url, title, and content
    """
    scraper = BlogScraper()
    urls = scraper.fetch_sitemap_urls()
    
    if not urls:
        print("⚠️ No URLs found")
        return []
    
    # Run async scraping
    posts = asyncio.run(scraper.scrape_all(urls))
    return posts
