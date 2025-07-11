"""
Text Extractor Module
Extracts clean text content from HTML pages using trafilatura and BeautifulSoup
"""

import trafilatura
from bs4 import BeautifulSoup
import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse

class TextExtractor:
    def __init__(self):
        """Initialize the text extractor"""
        self.unwanted_tags = {
            'script', 'style', 'nav', 'header', 'footer', 'aside', 
            'advertisement', 'ads', 'sidebar', 'menu', 'breadcrumb'
        }
        
        self.unwanted_classes = {
            'nav', 'navigation', 'menu', 'header', 'footer', 'sidebar',
            'advertisement', 'ads', 'social', 'share', 'comment',
            'breadcrumb', 'pagination', 'related'
        }
    
    def extract_content(self, html: str, url: str) -> Dict[str, any]:
        """
        Extract clean text content from HTML
        
        Args:
            html: HTML content
            url: Source URL for the HTML
            
        Returns:
            Dictionary with extracted content, title, and links
        """
        try:
            # Use trafilatura for main content extraction
            content = trafilatura.extract(html)
            
            # Fallback to BeautifulSoup if trafilatura fails
            if not content:
                content = self._extract_with_beautifulsoup(html)
            
            # Extract title and links using BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title = self._extract_title(soup)
            links = self._extract_links(soup, url)
            
            # Clean the content
            content = self._clean_text(content or "")
            
            return {
                'content': content,
                'title': title,
                'links': links
            }
            
        except Exception as e:
            # Fallback extraction
            return {
                'content': self._extract_with_beautifulsoup(html),
                'title': self._extract_title_fallback(html),
                'links': []
            }
    
    def _extract_with_beautifulsoup(self, html: str) -> str:
        """
        Extract text using BeautifulSoup as fallback
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text content
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted tags
            for tag in soup.find_all():
                # Remove by tag name
                if tag.name in self.unwanted_tags:
                    tag.decompose()
                    continue
                
                # Remove by class name
                tag_classes = tag.get('class', [])
                if any(cls.lower() in self.unwanted_classes for cls in tag_classes):
                    tag.decompose()
                    continue
                
                # Remove by id
                tag_id = tag.get('id', '').lower()
                if any(unwanted in tag_id for unwanted in self.unwanted_classes):
                    tag.decompose()
                    continue
            
            # Focus on main content areas
            main_content = None
            content_selectors = [
                'main', 'article', '[role="main"]', '.content', '#content',
                '.post', '.entry', '.story', '.article-body'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extract text
            text = main_content.get_text(separator=' ', strip=True)
            
            return text
            
        except Exception:
            return ""
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract page title from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Page title
        """
        try:
            # Try different title sources
            title_sources = [
                soup.find('title'),
                soup.find('h1'),
                soup.find('meta', attrs={'property': 'og:title'}),
                soup.find('meta', attrs={'name': 'title'})
            ]
            
            for source in title_sources:
                if source:
                    if source.name == 'meta':
                        title = source.get('content', '')
                    else:
                        title = source.get_text(strip=True)
                    
                    if title:
                        return self._clean_text(title)[:200]  # Limit title length
            
            return "Untitled"
            
        except Exception:
            return "Untitled"
    
    def _extract_title_fallback(self, html: str) -> str:
        """
        Fallback title extraction using regex
        
        Args:
            html: HTML content
            
        Returns:
            Page title
        """
        try:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if title_match:
                return self._clean_text(title_match.group(1))[:200]
            return "Untitled"
        except Exception:
            return "Untitled"
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from the page
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urljoin(base_url, href)
                    links.append(absolute_url)
        except Exception:
            pass
        
        return list(set(links))  # Remove duplicates
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted patterns
        patterns_to_remove = [
            r'cookie.*?policy',
            r'privacy.*?policy',
            r'terms.*?service',
            r'subscribe.*?newsletter',
            r'follow.*?social',
            r'advertisement',
            r'sponsored.*?content'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove excessive whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
