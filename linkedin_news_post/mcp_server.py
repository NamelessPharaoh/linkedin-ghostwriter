import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from exa_py import Exa

# Import configuration
from linkedin_news_post.config import (
    EXA_API_KEY,
    SEARCH_NUM_RESULTS,
    SEARCH_MAX_CHARACTERS,
    SEARCH_CATEGORY,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    logger
)

# Load environment variables from .env file
load_dotenv()

# Initialize MCP server
mcp = FastMCP("linkedin_tools_stdio")

# Initialize Exa client if API key is available
exa = None
if EXA_API_KEY:
    try:
        exa = Exa(api_key=EXA_API_KEY)
        logger.info("Exa client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Exa client: {str(e)}")

@mcp.tool()
def search_and_content(
    query: str,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None
) -> str:
    """
    Search for webpages based on the query and return their contents.
    
    Args:
        query: The search query string, focused on aviation maintenance and MRO topics
        start_published_date: Start date for published content in ISO format with .000Z suffix
        end_published_date: End date for published content in ISO format with .000Z suffix
        
    Returns:
        JSON string containing search results and their contents
        
    Raises:
        Exception: If the Exa API call fails or if the Exa client is not initialized
    """
    if not exa:
        error_msg = "Exa client not initialized. Please check EXA_API_KEY environment variable."
        logger.error(error_msg)
        return {"error": error_msg}
    
    try:
        # Use provided dates or defaults
        start_date = start_published_date or DEFAULT_START_DATE
        end_date = end_published_date or DEFAULT_END_DATE
        
        logger.info(f"Searching for '{query}' between {start_date} and {end_date}")
        
        return exa.search_and_contents(
            query,
            use_autoprompt=False,
            num_results=SEARCH_NUM_RESULTS,
            start_published_date=start_date,
            end_published_date=end_date,
            text={"max_characters": SEARCH_MAX_CHARACTERS},
            category=SEARCH_CATEGORY,
        )
    except Exception as e:
        error_msg = f"Error in search_and_content: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


if __name__ == "__main__":
    logger.info("Starting MCP server with tools: %s", mcp.list_tools())
    logger.info("Server configured for aviation maintenance and MRO content")
    mcp.run(transport="stdio")
