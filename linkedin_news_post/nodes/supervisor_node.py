import logging

from linkedin_news_post import State
from linkedin_news_post.config import logger, DOMAIN_FOCUS
from linkedin_news_post.chains import supervisor_chain

from langchain_core.messages import HumanMessage
from langgraph.constants import END
from langgraph.types import Command
from typing import Literal

def supervisor_node(state: State) -> Command[Literal["publisher_node", "researcher_node", "writer_node", "quality_node", "__end__"]]:
    """
    Supervisor node that coordinates the workflow and decides what to do next.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        Command to go to the next node in the workflow
    """
    try:
        # Log current state for debugging
        logger.debug(f"Current state messages count: {len(state['messages'])}")
        
        # Invoke supervisor chain to decide next step
        logger.info("Invoking supervisor chain to determine next step")
        result = supervisor_chain.invoke(state)
        logger.info(f"Supervisor decided next node: {result.next_node}")
        
        # Route to appropriate node based on supervisor decision
        if result.next_node == "researcher_node":
            return Command(
                goto="researcher_node",
                update={"messages": [HumanMessage(content=f"Passing to researcher to find news about {DOMAIN_FOCUS}...", name="supervisor_node")]}
            )
        
        elif result.next_node == "writer_node":
            return Command(
                goto="writer_node",
                update={"messages": [HumanMessage(content="Passing to writer to create LinkedIn post...", name="supervisor_node")]}
            )
        
        elif result.next_node == "quality_node":
            return Command(
                goto="quality_node",
                update={"messages": [HumanMessage(content="Passing to quality checker to verify uniqueness...", name="supervisor_node")]}
            )
        
        elif result.next_node == "publisher_node":
            return Command(
                goto="publisher_node",
                update={"messages": [HumanMessage(content="Passing to publisher to publish post...", name="supervisor_node")]}
            )
        
        elif result.next_node == "end_node":
            return Command(
                goto={END},
                update={"messages": [HumanMessage(content="Finishing the process...", name="supervisor_node")]}
            )
        
        else:
            # Handle unexpected node
            logger.error(f"Unexpected next_node value: {result.next_node}")
            return Command(
                goto={END},
                update={"messages": [HumanMessage(content=f"Error: Unexpected next node '{result.next_node}'", name="supervisor_node")]}
            )
            
    except Exception as e:
        error_message = f"Error in supervisor node: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Return error and end workflow
        return Command(
            goto={END},
            update={"messages": [HumanMessage(content=f"Error in workflow: {error_message}", name="supervisor_node")]}
        )
