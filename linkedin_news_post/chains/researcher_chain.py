import logging
from datetime import date
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import configuration
from linkedin_news_post.config import DEFAULT_MODEL, logger, DOMAIN_FOCUS

today = date.today()

class search_and_content(BaseModel):
    query: str = Field(description="Query for the search")
    start_published_date: str = Field(description="Start range of publishing range")
    end_published_date: str = Field(description="End range of publishing range")

# Initialize LLM with configurable model
try:
    llm = ChatOpenAI(model=DEFAULT_MODEL)
    logger.info(f"Initialized researcher chain LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize researcher chain LLM: {str(e)}")
    raise

try:
    llm_with_tools = llm.bind_tools([search_and_content])
    logger.info("Successfully bound tools to researcher chain LLM")
except Exception as e:
    logger.error(f"Failed to bind tools to researcher chain LLM: {str(e)}")
    raise

system = f"""You are an expert researcher tasked with finding the latest news in {DOMAIN_FOCUS} in the 1 to 3 months noting that today is {today} in the United States, tailored for aviation maintenance professionals and MRO operators. 

Select a topic and always call the tool "search_and_content" to find relevant content and output the result.

Focus on topics like:
- Regulatory changes affecting aircraft maintenance
- New technologies in MRO operations
- Industry best practices for aviation maintenance
- Safety protocols and updates
- Sustainability initiatives in aircraft maintenance
- Training and certification updates for maintenance technicians
- Supply chain developments affecting MRO operations

If the supervisor provides you with information, always try a different query to generate results that are as distinct as possible from the previous query.
"""

# Use placeholder instead of messages since we are working with create_react_agent
systemPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("placeholder", "{messages}"),
    ]
)

try:
    researcher_chain = systemPrompt | llm_with_tools
    logger.info("Researcher chain successfully created")
except Exception as e:
    logger.error(f"Failed to create researcher chain: {str(e)}")
    raise
