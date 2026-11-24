import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from dell_ai_util import ChatDellAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from tavily import TavilyClient

load_dotenv()
tavily = TavilyClient()

@tool
def search(query: str) -> str:
    """
    Tool that searches over internet
    Args:
        query: The query to search for
    Returns:
        The search result
    """
    print(f"Searching for {query}")
    return tavily.search(query=query)

def main():
    
    print("Hello from langchain-course!")
    # llm = ChatOllama(temperature=0, model="gemma3:270m")
    # llm = ChatOpenAI(temperature=0, model="gpt-5")
    # Initialize ChatDellAI with custom temperature and model
    #llm = ChatDellAI(temperature=0.7, model="gemma-4-e4b-it")
    llm = ChatDellAI(temperature=0, model="gpt-oss-120b")

    
   
    # Or use defaults from .env file:
    # llm = ChatDellAI()

    tools = [search]
    agent = create_agent(model=llm, tools=tools)
    result = agent.invoke({"messages": [HumanMessage(content="What is the weather in Tokyo?")]})
    print(result)
   

if __name__ == "__main__":
    main()
