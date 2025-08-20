from pocketflow import Flow
from nodes import (
    QuestionAnalysisNode,
    InitialCrawlNode,
    ContentAssessmentNode,
    LinkSelectionAgentNode,
    RecursiveCrawlNode,
    AnswerGenerationNode
)

def create_chatbot_flow():
    """Create and return an intelligent website chatbot flow."""
    # Create nodes
    question_analysis = QuestionAnalysisNode()
    initial_crawl = InitialCrawlNode()
    content_assessment = ContentAssessmentNode()
    link_selection = LinkSelectionAgentNode()
    recursive_crawl = RecursiveCrawlNode()
    answer_generation = AnswerGenerationNode()
    
    # Connect nodes with routing logic
    question_analysis.add_edge("initial_crawl", initial_crawl)
    initial_crawl.add_edge("content_assessment", content_assessment)
    content_assessment.add_edge("answer_generation", answer_generation)
    content_assessment.add_edge("link_selection", link_selection)
    link_selection.add_edge("recursive_crawl", recursive_crawl)
    link_selection.add_edge("answer_generation", answer_generation)
    recursive_crawl.add_edge("content_assessment", content_assessment)
    
    # Create flow starting with question analysis
    return Flow(start=question_analysis)

def initialize_shared_store(user_question: str, starting_url: str) -> dict:
    """Initialize the shared store with user input and default values."""
    return {
        "user_question": user_question,
        "starting_url": starting_url,
        "question_embedding": [],
        "question_analysis": "",
        "crawled_pages": {},
        "crawl_queue": [],
        "max_crawl_depth": 3,
        "current_depth": 0,
        "sufficient_content": False,
        "selected_links": [],
        "content_assessment": "",
        "final_answer": ""
    }

chatbot_flow = create_chatbot_flow()