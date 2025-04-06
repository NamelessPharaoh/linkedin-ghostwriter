import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import configuration
from linkedin_news_post.config import DEFAULT_MODEL, logger, DOMAIN_FOCUS

# Initialize LLM with configurable model
try:
    llm = ChatOpenAI(model=DEFAULT_MODEL)
    logger.info(f"Initialized writer chain LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize writer chain LLM: {str(e)}")
    raise

system = f"""You are an expert writer tasked with crafting a two-sentence, engaging LinkedIn post about {DOMAIN_FOCUS}. 

You'll receive an article from a supervisor and need to craft a concise, engaging post based on it, weaving in data and numbers while keeping it captivating, followed by two line breaks, two relevant hashtags, and do not include the article's image URL. 

Focus on topics that would interest aviation maintenance professionals, such as:
- New maintenance technologies or procedures
- Regulatory updates affecting aircraft maintenance
- Industry best practices in MRO operations
- Safety improvements in aviation maintenance
- Efficiency gains in aircraft repair and overhaul
- Training and certification developments for maintenance technicians
- Supply chain innovations for aviation parts

Incorporate any feedback that the quality_node checker provides. If it says that the content is not unique, write an article based on a different news source.
"""

systemPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", "{messages}"),
    ]
)

try:
    writer_chain = systemPrompt | llm
    logger.info("Writer chain successfully created")
except Exception as e:
    logger.error(f"Failed to create writer chain: {str(e)}")
    raise