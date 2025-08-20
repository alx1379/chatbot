from bs4 import BeautifulSoup
from typing import Dict, List
import re

def content_extractor(raw_html: str) -> Dict:
    """
    Extract and clean content from raw HTML.
    
    Args:
        raw_html: Raw HTML content
        
    Returns:
        Dict with {clean_text, title, links, images}
    """
    try:
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
            
        # Extract main content areas (prioritize main content)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I))
        if main_content:
            content_soup = main_content
        else:
            content_soup = soup
            
        # Extract clean text
        text = content_soup.get_text()
        # Clean up whitespace and normalize
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract links with context
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            if text and href:
                links.append({
                    'href': href,
                    'text': text,
                    'title': link.get('title', '')
                })
        
        # Extract images with alt text
        images = []
        for img in soup.find_all('img', src=True):
            images.append({
                'src': img['src'],
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
            
        return {
            'clean_text': clean_text,
            'title': title_text,
            'links': links,
            'images': images
        }
        
    except Exception as e:
        return {
            'clean_text': f"Error extracting content: {str(e)}",
            'title': "",
            'links': [],
            'images': []
        }

if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Navigation</nav>
            <main>
                <h1>Main Content</h1>
                <p>This is the main content of the page.</p>
                <a href="/link1">Link 1</a>
                <a href="/link2">Link 2</a>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    result = content_extractor(sample_html)
    print(f"Title: {result['title']}")
    print(f"Clean text: {result['clean_text'][:100]}...")
    print(f"Links: {len(result['links'])}")
