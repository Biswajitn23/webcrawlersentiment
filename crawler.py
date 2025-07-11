"""
Web Crawler Module
Handles crawling of web pages with domain restrictions and depth limits
"""

import requests
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import time
from typing import Set, Generator, Dict, Optional
import logging
from text_extractor import TextExtractor

class WebCrawler:
    def __init__(self, max_depth: int = 2, max_pages: int = 10, delay: float = 1.0, allow_external: bool = False):
        """
        Initialize the web crawler
        
        Args:
            max_depth: Maximum crawl depth
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
            allow_external: Whether to allow crawling external domains
        """
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.allow_external = allow_external
        self.visited: Set[str] = set()
        self.text_extractor = TextExtractor()
        
        # Setup session with proper headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0; +http://example.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL is valid for crawling
        
        Args:
            url: URL to check
            base_domain: Base domain for comparison
            
        Returns:
            True if URL is valid for crawling
        """
        try:
            parsed = urlparse(url)
            
            # Check if it's a valid HTTP/HTTPS URL
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check domain restriction
            if not self.allow_external and parsed.netloc != base_domain:
                return False
            
            # Skip common non-content files
            excluded_extensions = {
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.tar', '.gz', '.mp3', '.mp4', '.avi',
                '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
                '.css', '.js', '.xml', '.json'
            }
            
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in excluded_extensions):
                return False
            
            # Skip anchor links and fragments
            if parsed.fragment:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating URL {url}: {e}")
            return False
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragments and unnecessary parameters
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        # Remove fragment and rebuild URL
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        # Remove trailing slash for consistency (except for root)
        if normalized.endswith('/') and len(parsed.path) > 1:
            normalized = normalized[:-1]
            
        return normalized
    
    def fetch_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Fetch and extract content from a single page
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with page data or None if failed
        """
        try:
            self.logger.info(f"Fetching: {url}")
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Check if it's HTML content
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            # Extract text content and title
            extracted_data = self.text_extractor.extract_content(response.text, url)
            
            if not extracted_data['content'].strip():
                self.logger.warning(f"No content extracted from: {url}")
                return None
            
            return {
                'url': url,
                'title': extracted_data['title'],
                'content': extracted_data['content'],
                'links': extracted_data['links']
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            return None
    
    def crawl(self, start_url: str) -> Generator[Dict[str, str], None, None]:
        """
        Crawl pages starting from the given URL
        
        Args:
            start_url: Starting URL for crawling
            
        Yields:
            Dictionary containing page data
        """
        # Normalize starting URL
        start_url = self.normalize_url(start_url)
        base_domain = urlparse(start_url).netloc
        
        # Queue: (url, depth)
        crawl_queue = [(start_url, 0)]
        pages_crawled = 0
        
        self.logger.info(f"Starting crawl from: {start_url}")
        self.logger.info(f"Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        
        while crawl_queue and pages_crawled < self.max_pages:
            current_url, depth = crawl_queue.pop(0)
            
            # Skip if already visited
            if current_url in self.visited:
                continue
            
            # Skip if depth exceeded
            if depth > self.max_depth:
                continue
            
            # Mark as visited
            self.visited.add(current_url)
            
            # Fetch page content
            page_data = self.fetch_page(current_url)
            if not page_data:
                continue
            
            pages_crawled += 1
            self.logger.info(f"Crawled {pages_crawled}/{self.max_pages}: {current_url}")
            
            # Yield the page data
            yield {
                'url': page_data['url'],
                'title': page_data['title'],
                'content': page_data['content']
            }
            
            # Add new links to queue if we haven't reached max depth
            if depth < self.max_depth:
                for link in page_data['links']:
                    absolute_url = urljoin(current_url, link)
                    normalized_url = self.normalize_url(absolute_url)
                    
                    if (normalized_url not in self.visited and 
                        self.is_valid_url(normalized_url, base_domain)):
                        crawl_queue.append((normalized_url, depth + 1))
            
            # Respectful delay
            if self.delay > 0:
                time.sleep(self.delay)
        
        self.logger.info(f"Crawling completed. Total pages crawled: {pages_crawled}")
