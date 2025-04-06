import logging

from linkedin_news_post import State
from linkedin_news_post.config import logger, DOMAIN_FOCUS
from linkedin_news_post.chains import writer_chain

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from typing import Literal

def writer_node(state: State) -> Command[Literal["supervisor_node"]]:
    """
    Writer node that creates a LinkedIn post based on the research.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        Command to go to the supervisor node with the written post
    """
    try:
        # Invoke writer chain to create LinkedIn post
        logger.info(f"Creating LinkedIn post about {DOMAIN_FOCUS}")
        result = writer_chain.invoke(state)
        logger.info("Successfully created LinkedIn post")
        
        return Command(
            goto="supervisor_node",
            update={
                "messages": [HumanMessage(content=result.content, name="writer_node")]
            }
        )
    except Exception as e:
        error_message = f"Error in writer node: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Return error message to supervisor
        return Command(
            goto="supervisor_node",
            update={
                "messages": [HumanMessage(
                    content=f"Error creating LinkedIn post: {error_message}. Please try again.",
                    name="writer_node"
                )]
            }
        )
