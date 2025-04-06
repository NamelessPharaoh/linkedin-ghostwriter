import logging

from linkedin_news_post import State
from linkedin_news_post.config import logger, DOMAIN_FOCUS
from linkedin_news_post.chains import researcher_chain

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from typing import Literal

# Define the research prompt template
RESEARCH_PROMPT_TEMPLATE = "Tell me news about {domain} picking a topic of your choice"

def researcher_node(state: State) -> Command[Literal["tool_node"]]:
    """
    Researcher node that finds interesting news in the specified domain.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        Command to go to the tool node with the research result
    """
    try:
        # Create the research prompt using the domain focus
        research_prompt = RESEARCH_PROMPT_TEMPLATE.format(domain=DOMAIN_FOCUS)
        logger.info(f"Researching news about {DOMAIN_FOCUS}")
        
        # Add the research prompt to the messages
        new_messages = state["messages"] + [HumanMessage(content=research_prompt)]
        
        # Invoke the researcher chain
        logger.info("Invoking researcher chain")
        result = researcher_chain.invoke({
            "messages": new_messages
        })
        logger.info("Research completed successfully")
        
        return Command(
            goto="tool_node",
            update={
                "messages": [result]
            }
        )
    except Exception as e:
        error_message = f"Error in researcher node: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Return error message
        return Command(
            goto="tool_node",
            update={
                "messages": [HumanMessage(
                    content=f"Error researching {DOMAIN_FOCUS} news: {error_message}. Please try again.",
                    name="researcher_node"
                )]
            }
        )
