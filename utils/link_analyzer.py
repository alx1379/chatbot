from urllib.parse import urlparse, urljoin
from typing import List, Dict
import re

def link_analyzer(links: List[Dict], base_url: str, question_context: str) -> List[str]:
    """
    Analyze and prioritize links based on relevance to the question context.
    
    Args:
        links: List of link dictionaries with 'url' and 'text' keys
        base_url: Base URL for filtering same-domain links
        question_context: The user's question for relevance scoring
        
    Returns:
        List of prioritized relevant links (URLs only)
    """
    if not links:
        return []
    
    base_domain = urlparse(base_url).netloc
    question_lower = question_context.lower()
    
    # Extract keywords from question
    question_keywords = set(re.findall(r'\b\w+\b', question_lower))
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'where', 'when', 'why', 'who'}
    question_keywords = question_keywords - stop_words
    
    scored_links = []
    
    for link in links:
        url = link.get('url', '')
        text = link.get('text', '').lower()
        
        # Skip if no URL
        if not url:
            continue
            
        # Parse URL
        parsed_url = urlparse(url)
        
        # Skip external domains (focus on same site)
        if parsed_url.netloc and parsed_url.netloc != base_domain:
            continue
            
        # Skip non-HTTP links
        if not url.startswith(('http://', 'https://')):
            continue
            
        # Calculate relevance score
        score = 0
        
        # Score based on link text matching question keywords
        text_words = set(re.findall(r'\b\w+\b', text))
        keyword_matches = len(question_keywords.intersection(text_words))
        score += keyword_matches * 3
        
        # Score based on URL path relevance
        url_path = parsed_url.path.lower()
        url_words = set(re.findall(r'\b\w+\b', url_path))
        url_matches = len(question_keywords.intersection(url_words))
        score += url_matches * 2
        
        # Boost score for common helpful page types
        helpful_patterns = [
            r'\b(faq|help|support|about|contact|policy|return|shipping|guide|tutorial)\b',
            r'\b(documentation|docs|manual|instruction)\b',
            r'\b(service|product|feature|detail)\b'
        ]
        
        for pattern in helpful_patterns:
            if re.search(pattern, text) or re.search(pattern, url_path):
                score += 1
                
        # Penalize certain link types
        if re.search(r'\b(login|register|cart|checkout|account)\b', text) or \
           re.search(r'\b(login|register|cart|checkout|account)\b', url_path):
            score -= 2
            
        # Penalize file downloads
        if re.search(r'\.(pdf|doc|docx|xls|xlsx|zip|rar)$', url_path):
            score -= 1
            
        # Only include links with positive scores
        if score > 0:
            scored_links.append((url, score))
    
    # Sort by score (descending) and return top links
    scored_links.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 5 most relevant links
    return [link[0] for link in scored_links[:5]]

if __name__ == "__main__":
    # Test the link analyzer
    test_links = [
        {'url': 'https://example.com/about', 'text': 'About Us'},
        {'url': 'https://example.com/returns', 'text': 'Return Policy'},
        {'url': 'https://example.com/contact', 'text': 'Contact'},
        {'url': 'https://example.com/login', 'text': 'Login'},
        {'url': 'https://external.com/page', 'text': 'External Link'}
    ]
    
    question = "What is your return policy?"
    base_url = "https://example.com"
    
    relevant_links = link_analyzer(test_links, base_url, question)
    print(f"Relevant links: {relevant_links}")
