import os
import sys
from flow import chatbot_flow, initialize_shared_store

def main():
    """Main function to run the intelligent website chatbot."""
    print("🤖 Intelligent Website Chatbot")
    print("=" * 50)
    print("This chatbot can intelligently crawl websites to answer your questions.")
    print("It will start from a given URL and follow relevant links to find information.")
    print()
    
    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key to use this chatbot.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    try:
        # Get user input
        print("📝 Please provide the following information:")
        starting_url = input("Starting URL (e.g., https://example.com): ").strip()
        
        if not starting_url:
            print("❌ Starting URL is required!")
            return
            
        if not starting_url.startswith(('http://', 'https://')):
            print("❌ Please provide a valid URL starting with http:// or https://")
            return
        
        user_question = input("Your question: ").strip()
        
        if not user_question:
            print("❌ Question is required!")
            return
        
        print()
        print("🚀 Starting intelligent crawl and analysis...")
        print(f"📍 Starting URL: {starting_url}")
        print(f"❓ Question: {user_question}")
        print()
        
        # Initialize shared store
        shared = initialize_shared_store(user_question, starting_url)
        
        # Run the chatbot flow
        print("🔄 Processing...")
        result = chatbot_flow.run(shared)
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 CRAWLING SUMMARY")
        print("=" * 50)
        
        crawled_pages = shared.get("crawled_pages", {})
        print(f"📄 Pages crawled: {len(crawled_pages)}")
        print(f"🔍 Max depth reached: {shared.get('current_depth', 0)}")
        
        if crawled_pages:
            print("\n📋 Crawled URLs:")
            for i, (url, page_data) in enumerate(crawled_pages.items(), 1):
                relevance = page_data.get('relevance_score', 0)
                depth = page_data.get('crawl_depth', 0)
                print(f"  {i}. {url}")
                print(f"     └─ Relevance: {relevance:.3f}, Depth: {depth}")
        
        print("\n" + "=" * 50)
        print("🎯 FINAL ANSWER")
        print("=" * 50)
        
        final_answer = shared.get("final_answer", "No answer generated.")
        print(final_answer)
        
        print("\n" + "=" * 50)
        print("✅ Analysis complete!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your inputs and try again.")
        sys.exit(1)

def demo():
    """Run a demo with predefined inputs for testing."""
    print("🧪 Running demo mode...")
    
    # Demo inputs
    demo_url = "https://example.com"
    demo_question = "What is this website about?"
    
    print(f"📍 Demo URL: {demo_url}")
    print(f"❓ Demo Question: {demo_question}")
    print()
    
    # Initialize and run
    shared = initialize_shared_store(demo_question, demo_url)
    
    try:
        chatbot_flow.run(shared)
        print("✅ Demo completed successfully!")
        print(f"Answer: {shared.get('final_answer', 'No answer')}")
    except Exception as e:
        import traceback
        print(f"❌ Demo failed: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        main()
