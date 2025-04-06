import asyncio
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from composio_langchain import ComposioToolSet # Try importing from langchain adapter
from langchain_openai import OpenAIEmbeddings

from linkedin_news_post import State
from linkedin_news_post.nodes import (
    publisher_node, supervisor_node, researcher_node, writer_node, quality_node
)
from linkedin_news_post.mongo_store import MongoDBBaseStore
from linkedin_news_post.config import (
    MONGODB_URI, COMPOSIO_MCP_URL, DB_NAME, COLLECTION_NAME, logger, DOMAIN_FOCUS,
    COMPOSIO_LINKEDIN_TOOL, ORGANIZATION_URN, COMPOSIO_LINKEDIN_APP, COMPOSIO_LINKEDIN_ENTITY
)

# Load environment variables
load_dotenv()

# Check for required environment variables
if not MONGODB_URI:
    logger.error("MONGODB_URI environment variable is not set. MongoDB store will not function correctly.")

if not COMPOSIO_MCP_URL:
    logger.error("COMPOSIO_MCP_URL environment variable is not set. MCP client will not function correctly.")

if not COMPOSIO_LINKEDIN_TOOL:
    logger.error("COMPOSIO_LINKEDIN_TOOL environment variable is not set. LinkedIn integration will not function correctly.")

# Initialize OpenAI embeddings
openai_embeddings = OpenAIEmbeddings()
logger.info(f"Configured for domain focus: {DOMAIN_FOCUS}")

def embed_text(text: str) -> list[float]:
    return openai_embeddings.embed_query(text)

index_config = {
    "embed": embed_text,     
    "fields": ["content.article", "summary"],
    "index_name": "store_index",
}

# Initialize MongoDB store if connection string is available
mongo_store = None
if MONGODB_URI:
    try:
        mongo_store = MongoDBBaseStore(
            mongo_url=MONGODB_URI,
            db_name=DB_NAME,
            collection_name=COLLECTION_NAME,
            index_config=index_config,
            ttl_support=True
        )
        logger.info(f"MongoDB store initialized with database '{DB_NAME}' and collection '{COLLECTION_NAME}'")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB store: {str(e)}")

# Removed verify_linkedin_integration function

@asynccontextmanager
async def make_graph():
    """
    Create and configure the workflow graph with MCP client connections.
    
    Returns:
        A compiled workflow graph ready for execution.
    """
    if not mongo_store:
        logger.error("Cannot create graph: MongoDB store is not initialized")
        raise ValueError("MongoDB store is not initialized. Check MONGODB_URI environment variable.")
        
    if not COMPOSIO_MCP_URL:
        logger.error("Cannot create graph: COMPOSIO_MCP_URL is not set")
        raise ValueError("COMPOSIO_MCP_URL is not set. Check environment variables.")

    # Initialize Composio ToolSet using API Key from environment
    composio_api_key = os.getenv("COMPOSIO_API_KEY")
    if not composio_api_key:
        logger.error("COMPOSIO_API_KEY environment variable not set. Cannot initialize ComposioToolSet.")
        raise ValueError("COMPOSIO_API_KEY environment variable not set.")
    # Initialize ComposioToolSet (removed apps filter based on warning)
    mcp_client = ComposioToolSet(api_key=composio_api_key)
    logger.info(f"Composio ToolSet initialized.")

    # Fetch tools for the specified LinkedIn app using get_tools
    tools = [] # Default to empty list
    try:
        # Attempt to get tools filtered by app name
        # Assuming get_tools exists on the ComposioToolSet from composio_langchain
        tools = mcp_client.get_tools(apps=[COMPOSIO_LINKEDIN_APP])
        logger.info(f"Successfully fetched tools for app '{COMPOSIO_LINKEDIN_APP}': {[t.name for t in tools]}")
    except Exception as e:
         logger.error(f"Failed to get tools for app '{COMPOSIO_LINKEDIN_APP}': {e}", exc_info=True)
         # Continue with empty tools list if fetching fails

    # Create workflow graph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("supervisor_node", supervisor_node)
    # Pass the fetched list of tools to ToolNode
    workflow.add_node("tool_node", ToolNode(tools))
    workflow.add_node("publisher_node", publisher_node)
    workflow.add_node("researcher_node", researcher_node)
    workflow.add_node("quality_node", quality_node)
    workflow.add_node("writer_node", writer_node)

    # Add edges
    workflow.add_edge(START, "supervisor_node")
    workflow.add_edge("tool_node", "supervisor_node")

    # Compile graph with MongoDB store
    graph = workflow.compile(store=mongo_store)
    logger.info(f"Graph compiled successfully for {DOMAIN_FOCUS} content")
    yield graph

# Removed the orphaned except block and fixed indentation
