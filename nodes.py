from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.web_scraper import web_scraper
from utils.content_embedder import content_embedder
from utils.similarity_calculator import similarity_calculator
from utils.link_analyzer import link_analyzer

class QuestionAnalysisNode(Node):
    """Analyze user question to extract key information requirements and create embeddings"""
    
    def prep(self, shared):
        return shared["user_question"]
    
    def exec(self, user_question):
        # Analyze question with LLM
        analysis_prompt = f"""
        Analyze this user question and extract key information:
        Question: "{user_question}"
        
        Provide:
        1. Question type (factual, procedural, policy, etc.)
        2. Key concepts and keywords
        3. What type of information would be needed to answer this
        
        Format as JSON with keys: type, keywords, info_needed
        """
        
        analysis = call_llm(analysis_prompt)
        
        # Generate question embedding
        question_embedding = content_embedder(user_question)
        
        return {
            "analysis": analysis,
            "embedding": question_embedding
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["question_analysis"] = exec_res["analysis"]
        shared["question_embedding"] = exec_res["embedding"]
        return "initial_crawl"

class InitialCrawlNode(Node):
    """Crawl the starting webpage and extract structured content"""
    
    def prep(self, shared):
        return shared["starting_url"]
    
    def exec(self, starting_url):
        # Scrape the initial page
        page_data = web_scraper(starting_url)
        return page_data
    
    def post(self, shared, prep_res, exec_res):
        # Initialize crawled pages and crawl queue
        shared["crawled_pages"] = {
            exec_res["url"]: {
                **exec_res,
                "crawl_depth": 0,
                "relevance_score": 0.0
            }
        }
        
        # Extract links for crawl queue
        links = exec_res.get("links", [])
        shared["crawl_queue"] = [link["url"] for link in links[:10]]  # Limit initial queue
        shared["current_depth"] = 0
        
        return "content_assessment"

class ContentAssessmentNode(Node):
    """Determine if current crawled content contains sufficient information to answer the question"""
    
    def prep(self, shared):
        return {
            "crawled_pages": shared["crawled_pages"],
            "question_embedding": shared["question_embedding"],
            "user_question": shared["user_question"]
        }
    
    def exec(self, prep_data):
        crawled_pages = prep_data["crawled_pages"]
        question_embedding = prep_data["question_embedding"]
        user_question = prep_data["user_question"]
        
        # Calculate relevance scores for all pages
        total_relevance = 0
        page_count = 0
        
        for url, page_data in crawled_pages.items():
            content = page_data.get("content", "")
            if content and content != "Error":
                # Generate content embedding
                content_embedding = content_embedder(content[:2000])  # Limit for embedding
                relevance_score = similarity_calculator(question_embedding, content_embedding)
                page_data["relevance_score"] = relevance_score
                total_relevance += relevance_score
                page_count += 1
        
        avg_relevance = total_relevance / page_count if page_count > 0 else 0
        
        # Use LLM to assess if content is sufficient
        all_content = "\n\n".join([
            f"Page: {url}\nContent: {page['content'][:500]}..."
            for url, page in crawled_pages.items()
            if page.get("content") and page["content"] != "Error"
        ])
        
        assessment_prompt = f"""
        Question: "{user_question}"
        
        Available content from crawled pages:
        {all_content}
        
        Can this content adequately answer the user's question? 
        Consider:
        - Is the information complete?
        - Is it directly relevant?
        - Are there gaps that need more information?
        
        Respond with: SUFFICIENT or INSUFFICIENT
        If INSUFFICIENT, briefly explain what additional information is needed.
        """
        
        assessment = call_llm(assessment_prompt)
        sufficient = "SUFFICIENT" in assessment.upper()
        
        return {
            "sufficient": sufficient,
            "assessment": assessment,
            "avg_relevance": avg_relevance
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["sufficient_content"] = exec_res["sufficient"]
        shared["content_assessment"] = exec_res["assessment"]
        
        # Update crawled pages with relevance scores
        for url, page_data in shared["crawled_pages"].items():
            if "relevance_score" in page_data:
                shared["crawled_pages"][url] = page_data
        
        if exec_res["sufficient"] or shared["current_depth"] >= shared.get("max_crawl_depth", 3):
            return "answer_generation"
        else:
            return "link_selection"

class LinkSelectionAgentNode(Node):
    """Intelligently select which links to follow next based on question context and link relevance"""
    
    def prep(self, shared):
        return {
            "crawl_queue": shared.get("crawl_queue", []),
            "question_analysis": shared.get("question_analysis", ""),
            "user_question": shared["user_question"],
            "current_depth": shared["current_depth"],
            "max_crawl_depth": shared.get("max_crawl_depth", 3),
            "crawled_pages": shared["crawled_pages"]
        }
    
    def exec(self, prep_data):
        if prep_data["current_depth"] >= prep_data["max_crawl_depth"]:
            return []
        
        crawl_queue = prep_data["crawl_queue"]
        user_question = prep_data["user_question"]
        crawled_pages = prep_data["crawled_pages"]
        
        # Get all available links from crawled pages
        all_links = []
        for page_data in crawled_pages.values():
            page_links = page_data.get("links", [])
            all_links.extend(page_links)
        
        # Filter out already crawled URLs
        crawled_urls = set(crawled_pages.keys())
        new_links = [link for link in all_links if link.get("url") not in crawled_urls]
        
        if not new_links:
            return []
        
        # Use link analyzer to get relevant links
        base_url = list(crawled_pages.keys())[0]  # Use first crawled URL as base
        relevant_links = link_analyzer(new_links, base_url, user_question)
        
        # Limit to top 3 links per crawl iteration
        return relevant_links[:3]
    
    def post(self, shared, prep_res, exec_res):
        if exec_res:
            shared["selected_links"] = exec_res
            return "recursive_crawl"
        else:
            return "answer_generation"

class RecursiveCrawlNode(BatchNode):
    """Crawl selected links and add their content to the knowledge base"""
    
    def prep(self, shared):
        return {
            "selected_links": shared.get("selected_links", []),
            "current_depth": shared["current_depth"]
        }
    
    def exec(self, prep_data):
        selected_links = prep_data["selected_links"]
        current_depth = prep_data["current_depth"]
        
        # Crawl each selected link
        results = []
        for url in selected_links:
            page_data = web_scraper(url)
            page_data["crawl_depth"] = current_depth + 1
            results.append(page_data)
        
        return results
    
    def post(self, shared, prep_res, exec_res):
        # Add new pages to crawled_pages
        for page_data in exec_res:
            if page_data and page_data.get("url"):
                shared["crawled_pages"][page_data["url"]] = page_data
        
        # Increment depth
        shared["current_depth"] += 1
        
        return "content_assessment"

class AnswerGenerationNode(Node):
    """Synthesize final answer using all collected relevant content"""
    
    def prep(self, shared):
        return {
            "crawled_pages": shared["crawled_pages"],
            "user_question": shared["user_question"]
        }
    
    def exec(self, prep_data):
        crawled_pages = prep_data["crawled_pages"]
        user_question = prep_data["user_question"]
        
        # Sort pages by relevance score
        sorted_pages = sorted(
            crawled_pages.items(),
            key=lambda x: x[1].get("relevance_score", 0),
            reverse=True
        )
        
        # Compile relevant content
        relevant_content = []
        for url, page_data in sorted_pages:
            if page_data.get("relevance_score", 0) > 0.1:  # Only include reasonably relevant content
                content = page_data.get("content", "")
                if content and content != "Error":
                    relevant_content.append(f"From {url}:\n{content[:1000]}...")
        
        if not relevant_content:
            return "I couldn't find sufficient relevant information to answer your question. Please try a different question or provide a more specific starting URL."
        
        # Generate comprehensive answer
        answer_prompt = f"""
        Question: "{user_question}"
        
        Based on the following information gathered from the website:
        
        {chr(10).join(relevant_content)}
        
        Please provide a comprehensive and accurate answer to the user's question. 
        Use only the information provided above. If the information is incomplete, 
        acknowledge what you found and what might be missing.
        
        Include relevant details and be specific where possible.
        """
        
        answer = call_llm(answer_prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        shared["final_answer"] = exec_res
        return "complete"