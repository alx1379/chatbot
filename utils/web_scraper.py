import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Dict, List, Optional
from config import Config

def web_scraper(url: str, max_content_length: int = None) -> Dict:
    """
    Scrape a webpage and extract structured content.
    
    Args:
        url: The URL to scrape
        max_content_length: Maximum length of content to extract
        
    Returns:
        Dict with {url, title, content, links, metadata}
    """
    try:
        # Use max_content_length from config if not provided
        if max_content_length is None:
            max_content_length = Config.MAX_CONTENT_LENGTH
            
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': Config.USER_AGENT
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Extract main content
        content = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit content length
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(url, href)
            link_text = link.get_text().strip()
            if link_text and absolute_url.startswith(('http://', 'https://')):
                links.append({
                    'url': absolute_url,
                    'text': link_text
                })
        
        # Extract metadata
        metadata = {
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'content_length': len(content),
            'num_links': len(links),
            'domain': urlparse(url).netloc
        }
        
        return {
            'url': url,
            'title': title_text,
            'content': content,
            'links': links,
            'metadata': metadata
        }
        
    except requests.RequestException as e:
        return {
            'url': url,
            'title': "Error",
            'content': f"Failed to scrape URL: {str(e)}",
            'links': [],
            'metadata': {'error': str(e)}
        }

if __name__ == "__main__":
    # Test the scraper
    test_url = "https://example.com"
    result = web_scraper(test_url)
    print(f"Title: {result['title']}")
    print(f"Content length: {len(result['content'])}")
    print(f"Number of links: {len(result['links'])}")
