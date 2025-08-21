from openai import OpenAI
from config import Config

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_llm(prompt):    
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    r = client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
    
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
