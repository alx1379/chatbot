import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to manage all environment variables and settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Crawling Configuration
    MAX_CRAWL_DEPTH = int(os.getenv("MAX_CRAWL_DEPTH", "3"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
    MAX_LINKS_PER_PAGE = int(os.getenv("MAX_LINKS_PER_PAGE", "10"))
    MAX_LINKS_TO_CRAWL = int(os.getenv("MAX_LINKS_TO_CRAWL", "3"))
    
    # Request Configuration
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Content Processing Configuration
    MIN_RELEVANCE_SCORE = float(os.getenv("MIN_RELEVANCE_SCORE", "0.1"))
    EMBEDDING_MAX_CHARS = int(os.getenv("EMBEDDING_MAX_CHARS", "8000"))
    CONTENT_PREVIEW_CHARS = int(os.getenv("CONTENT_PREVIEW_CHARS", "2000"))
    
    # Debug Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file or environment variables.")
        
        if cls.MAX_CRAWL_DEPTH < 1:
            raise ValueError("MAX_CRAWL_DEPTH must be at least 1")
            
        if cls.MAX_CONTENT_LENGTH < 1000:
            raise ValueError("MAX_CONTENT_LENGTH must be at least 1000 characters")
    
    @classmethod
    def get_summary(cls):
        """Get a summary of current configuration (without sensitive data)."""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "embedding_model": cls.OPENAI_EMBEDDING_MODEL,
            "max_crawl_depth": cls.MAX_CRAWL_DEPTH,
            "max_content_length": cls.MAX_CONTENT_LENGTH,
            "max_links_per_page": cls.MAX_LINKS_PER_PAGE,
            "max_links_to_crawl": cls.MAX_LINKS_TO_CRAWL,
            "request_timeout": cls.REQUEST_TIMEOUT,
            "min_relevance_score": cls.MIN_RELEVANCE_SCORE,
            "debug": cls.DEBUG,
            "verbose_logging": cls.VERBOSE_LOGGING,
            "api_key_set": bool(cls.OPENAI_API_KEY)
        }

# Validate configuration on import
Config.validate()
