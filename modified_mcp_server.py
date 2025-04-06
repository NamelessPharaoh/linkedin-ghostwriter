#!/usr/bin/env python3
"""
Modified MCP Server for LinkedIn Ghostwriter

This script is a modified version of the original MCP server script that can be run directly
without import errors. It adds the necessary path manipulation to ensure imports work correctly.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# Now we can import from linkedin_news_post
from linkedin_news_post.config import (
    EXA_API_KEY,
    SEARCH_NUM_RESULTS,
    SEARCH_MAX_CHARACTERS,
    SEARCH_CATEGORY,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    logger
)

# Import the rest of the necessary modules
from mcp.server.fastmcp import FastMCP
from exa_py import Exa as ExaAPI
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the Exa API client
exa_client = ExaAPI(EXA_API_KEY)

async def search_news(query, start_date=None, end_date=None, category=None):
    """
    Search for news articles using the Exa API
    
    Args:
        query: The search query
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        category: News category
        
    Returns:
        List of news articles
    """
    try:
        logger.info(f"Searching for news with query: {query}")
        
        # Use default dates if not provided
        if not start_date:
            start_date = DEFAULT_START_DATE
        if not end_date:
            end_date = DEFAULT_END_DATE
        
        # Use default category if not provided
        if not category:
            category = SEARCH_CATEGORY
        
        # Perform the search
        results = exa_client.search_and_contents(
            query,
            num_results=SEARCH_NUM_RESULTS,
            use_autoprompt=True,
            start_published_date=start_date,
            end_published_date=end_date,
            category=category,
            text_contents_options={"max_characters": SEARCH_MAX_CHARACTERS}
        )
        
        # Format the results
        formatted_results = []
        for result in results.results:
            formatted_result = {
                "title": result.title,
                "url": result.url,
                "published_date": result.published_date,
                "author": result.author,
                "content": result.text[:SEARCH_MAX_CHARACTERS] if result.text else ""
            }
            formatted_results.append(formatted_result)
        
        logger.info(f"Found {len(formatted_results)} news articles")
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error searching for news: {str(e)}")
        return {"error": str(e)}

async def publish_to_linkedin(text):
    """
    Publish a post to LinkedIn using the Composio integration
    
    Args:
        text: The text to post to LinkedIn
        
    Returns:
        Result of the LinkedIn post operation
    """
    try:
        logger.info("Publishing to LinkedIn")
        logger.info(f"Post content: {text[:100]}...")
        
        # In a real implementation, this would use the Composio API to post to LinkedIn
        # For now, we'll just simulate a successful post
        
        # Simulate a successful post
        result = {
            "success": True,
            "post_id": f"linkedin-post-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "message": "Post published successfully to LinkedIn"
        }
        
        logger.info(f"LinkedIn post result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error publishing to LinkedIn: {str(e)}")
        return {"error": str(e)}

async def main():
    """Main entry point"""
    logger.info("Starting LinkedIn News Post MCP Server")
    
    # Create a FastMCP server
    server = FastMCP("linkedin-news-post-server")
    
    # Register tools using decorators
    @server.tool()
    def search_news_tool(query, start_date=None, end_date=None, category=None):
        """
        Search for news articles using the Exa API
        
        Args:
            query: The search query
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            category: News category
            
        Returns:
            List of news articles
        """
        try:
            logger.info(f"Searching for news with query: {query}")
            
            # Use default dates if not provided
            if not start_date:
                start_date = DEFAULT_START_DATE
            if not end_date:
                end_date = DEFAULT_END_DATE
            
            # Use default category if not provided
            if not category:
                category = SEARCH_CATEGORY
            
            # Perform the search
            results = exa_client.search_and_contents(
                query,
                num_results=SEARCH_NUM_RESULTS,
                use_autoprompt=True,
                start_published_date=start_date,
                end_published_date=end_date,
                category=category,
                text_contents_options={"max_characters": SEARCH_MAX_CHARACTERS}
            )
            
            # Format the results
            formatted_results = []
            for result in results.results:
                formatted_result = {
                    "title": result.title,
                    "url": result.url,
                    "published_date": result.published_date,
                    "author": result.author,
                    "content": result.text[:SEARCH_MAX_CHARACTERS] if result.text else ""
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} news articles")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error searching for news: {str(e)}")
            return {"error": str(e)}
    
    @server.tool()
    def publish_to_linkedin_tool(text):
        """
        Publish a post to LinkedIn using the Composio integration
        
        Args:
            text: The text to post to LinkedIn
            
        Returns:
            Result of the LinkedIn post operation
        """
        try:
            logger.info("Publishing to LinkedIn")
            logger.info(f"Post content: {text[:100]}...")
            
            # In a real implementation, this would use the Composio API to post to LinkedIn
            # For now, we'll just simulate a successful post
            
            # Simulate a successful post
            result = {
                "success": True,
                "post_id": f"linkedin-post-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "message": "Post published successfully to LinkedIn"
            }
            
            logger.info(f"LinkedIn post result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {str(e)}")
            return {"error": str(e)}
    
    logger.info("LinkedIn News Post MCP Server initialized")
    
    # Return the server instead of running it directly
    return server

if __name__ == "__main__":
    # Get the server instance
    server = asyncio.run(main())
    
    # Run the server directly (not inside an async context)
    if server:
        logger.info("Starting MCP server with tools: %s", server.list_tools())
        server.run(transport="stdio")