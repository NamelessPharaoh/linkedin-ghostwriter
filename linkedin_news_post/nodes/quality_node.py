import logging

from linkedin_news_post import State
from linkedin_news_post.config import DEFAULT_SEARCH_LIMIT, logger, DOMAIN_FOCUS
from linkedin_news_post.chains import quality_chain

from langgraph.types import Command
from langgraph.store.base import BaseStore
from langchain_core.messages import HumanMessage
from typing import Literal

def quality_node(state: State, store: BaseStore) -> Command[Literal["supervisor_node"]]:
    """
    Quality node that checks if the proposed article is unique compared to past articles.
    
    Args:
        state: The current state of the workflow
        store: The store containing past articles
        
    Returns:
        Command to go to the supervisor node with the quality check result
    """
    try:
        # Semantic search using proposed article
        logger.info("Performing semantic search for similar past articles")
        past_articles = store.search(
            ("articles",), 
            query=state["messages"][-2].content, 
            limit=DEFAULT_SEARCH_LIMIT
        )
        logger.info(f"Found {len(past_articles)} potentially similar past articles")
        
        # Invoke quality chain to check uniqueness
        logger.info("Invoking quality chain to check article uniqueness")
        result = quality_chain.invoke({
            "messages": state["messages"],
            "past_articles": past_articles
        })
        logger.info("Quality check completed")
        
        return Command(
            goto="supervisor_node",
            update={"messages": [HumanMessage(content=result.content, name="quality_node")]}
        )
    except Exception as e:
        error_message = f"Error in quality node: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        # Return error message to supervisor
        return Command(
            goto="supervisor_node",
            update={"messages": [HumanMessage(
                content=f"Error checking article uniqueness: {error_message}. Please try again with a different article about {DOMAIN_FOCUS}.",
                name="quality_node"
            )]}
        )