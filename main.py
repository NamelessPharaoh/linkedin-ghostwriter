import asyncio
import os               # Added import
import sys              # Added import
from dotenv import load_dotenv # Added import
from composio_langchain import ComposioToolSet, App # Added import

from linkedin_news_post.graph import make_graph


# Define the check function (adapted from previous attempt in run_app.py)
def check_composio_connection():
    """Check if the Composio LinkedIn connection is active."""
    print("Checking Composio LinkedIn connection...")
    try:
        # Ensure COMPOSIO_API_KEY is set (should be loaded by load_dotenv)
        api_key = os.getenv("COMPOSIO_API_KEY")
        if not api_key:
             print("[ERROR] COMPOSIO_API_KEY environment variable not set.")
             print("Please set your Composio API key in the .env file and try again.")
             return False

        # Pass the API key explicitly if needed, though ToolSet might pick it up from env
        composio_toolset = ComposioToolSet(api_key=api_key)
        # Attempt to get tools for LinkedIn. This implicitly checks the connection.
        # Use App.LINKEDIN (adjust if Composio uses a different enum name)
        tools = composio_toolset.get_tools(apps=[App.LINKEDIN])
        if not tools:
             print("[WARN] Composio returned no tools for LinkedIn, but no error. Connection might be present but inactive or misconfigured.")
             print("[INFO] Proceeding, but verify LinkedIn connection in Composio dashboard if issues arise.")
             # Consider returning False here if having tools is strictly required for the app to function.
             return True

        print("[INFO] Composio LinkedIn connection appears active.")
        return True
    except Exception as e:
        error_message = str(e)
        # Check for the specific connection error message
        if "Could not find a connection" in error_message or "No active connection found" in error_message:
            print("\n[ERROR] Active Composio connection for LinkedIn not found.")
            print("Please set up the connection using the Composio CLI:")
            print("  1. Log in: `composio login`")
            print("  2. Add LinkedIn: `composio add linkedin` (and complete browser authorization)")
            print("Exiting application.\n")
            return False
        else:
            # Handle other potential errors during tool retrieval
            print(f"[ERROR] Failed to check Composio connection: {error_message}")
            print("Please ensure your Composio API key is correct and Composio services are reachable.")
            return False

async def run_graph():
    # The connection check is now done before this function is called
    async with make_graph() as graph:
        print("[INFO] Invoking LangGraph...") # Added info message
        await graph.ainvoke({"messages": [
            ("user", "Publish a linkedin article")
        ]})
        print("[INFO] LangGraph invocation complete.") # Added info message


# --- Main execution block ---
if __name__ == "__main__":
    # Load environment variables from .env file first
    load_dotenv()
    print("[INFO] Loaded environment variables from .env file.")

    # Perform Composio connection check
    if not check_composio_connection():
        sys.exit(1) # Exit if connection check fails

    # Run the main async function
    try:
        asyncio.run(run_graph())
    except Exception as e:
        print(f"[ERROR] An error occurred during graph execution: {e}")
        sys.exit(1)