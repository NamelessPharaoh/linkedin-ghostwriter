import logging
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Import configuration
from linkedin_news_post.config import DEFAULT_MODEL, logger, DOMAIN_FOCUS

# Initialize LLM with configurable model
try:
    llm = ChatOpenAI(model=DEFAULT_MODEL)
    logger.info(f"Initialized supervisor chain LLM with model: {DEFAULT_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize supervisor chain LLM: {str(e)}")
    raise

class Handout(BaseModel):
    next_node: Literal["researcher_node", "writer_node", "publisher_node", "quality_node", "end_node"] = Field(
        description="Next node in the workflow"
    )

try:
    structured_llm = llm.with_structured_output(Handout)
    logger.info("Successfully configured structured output for supervisor chain")
except Exception as e:
    logger.error(f"Failed to configure structured output: {str(e)}")
    raise

system = f"""You are a supervisor tasked with managing a conversation between the following workers: writer_node, quality_node, researcher_node, and publisher_node. You should refer to each worker at least once. Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status. When the post has been successfully published respond with "end_node". 

The workflow is focused on creating LinkedIn posts about {DOMAIN_FOCUS}.

# Note:
 - Listen to the recommendations of the quality_node
 - Be ready to suggest different queries to the researcher
 - Ensure content is relevant to aviation maintenance professionals
 - Prioritize topics related to aircraft maintenance, MRO operations, and aviation safety
 - Ensure posts provide value to professionals in the aviation maintenance industry
"""

systemPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("user", "{messages}"),
    ]
)

try:
    supervisor_chain = systemPrompt | structured_llm
    logger.info("Supervisor chain successfully created")
except Exception as e:
    logger.error(f"Failed to create supervisor chain: {str(e)}")
    raise
