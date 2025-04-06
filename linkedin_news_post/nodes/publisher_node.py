import os
import logging

from linkedin_news_post import State
from linkedin_news_post.config import DEFAULT_MODEL, logger, DOMAIN_FOCUS
from linkedin_news_post.chains import publisher_chain

from langgraph.constants import END
from langgraph.types import Command
from typing import Literal
from langgraph.store.base import BaseStore

from pydantic import BaseModel, Field
from langmem import create_memory_store_manager

class Article(BaseModel):
    article: str = Field(description="Very concise description of what the published article is about")

def publisher_node(state: State, store: BaseStore) -> Command[Literal["tool_node"]]:
    # Memory Management
    try:
        manager = create_memory_store_manager(
            DEFAULT_MODEL,
            namespace=("articles",),
            schemas=[Article],
            instructions=f"Extract the information from the most recent article written by the writer_node message, which will be the newly published article about {DOMAIN_FOCUS}. Add 1 new entry for the article to the collection, including details such as dates and statistics for future reference, while avoiding content redundancy.",
            store=store,
            enable_inserts=True
        )
        
        manager.invoke({"messages": state["messages"]})
        logger.info("Successfully managed memory store for articles")
    except Exception as e:
        logger.error(f"Error in memory management: {str(e)}", exc_info=True)
        # Continue execution even if memory management fails

    logger.info("Invoking publisher_chain with state")
    try:
        result = publisher_chain.invoke(state)
        logger.info("Publisher chain result: %s", result)
    except Exception as e:
        logger.error("Error invoking publisher_chain: %s", str(e), exc_info=True)
        raise

    return Command(
        goto="tool_node",
        update={
            "messages": [result]
        }
    )