import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI, ChatOpenAI
from dell_ai_util import ChatDellAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from typing import List
from pydantic import BaseModel, Field

class Source(BaseModel):
    """Schema for a source used by the agent"""
    url: str = Field(description="The URL of the source")
    

class AgentResponse(BaseModel):
    """Schema for the agent response with answer and sources"""
    answer: str = Field(description="The agent's answer to the query")
    sources: List[Source] = Field(default_factory=list,  description="List of sources used to generate the answer")


load_dotenv()

def main():
    
    print("Hello from langchain-course!")
    # llm = ChatOllama(temperature=0, model="gemma3:270m")
    # llm = ChatOpenAI(temperature=0, model="gpt-5")
    # Initialize ChatDellAI with custom temperature and model
    #llm = ChatDellAI(temperature=0.7, model="gemma-4-e4b-it")
    llm = ChatDellAI(temperature=0, model="gpt-oss-120b")
   
    # Or use defaults from .env file:
    # llm = ChatDellAI()

    tools = [TavilySearch()]
    agent = create_agent(model=llm, tools=tools, response_format=AgentResponse)
    result = agent.invoke({"messages": [HumanMessage(content="search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details?")]})
    print(result)
   

if __name__ == "__main__":
    main()
