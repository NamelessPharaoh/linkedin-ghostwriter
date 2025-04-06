#!/usr/bin/env python3
"""
Direct runner script for LinkedIn Ghostwriter application.
This script directly imports and runs the necessary components
without using subprocesses, avoiding Python path issues.
"""

import os
import sys
import time
import asyncio
import threading
import importlib.util
from pathlib import Path

# Ensure the current directory is in the Python path
sys.path.insert(0, os.getcwd())

def import_module_from_file(module_name, file_path):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_mcp_server():
    """Run the MCP server in a separate thread"""
    print("Starting MCP server...")
    
    try:
        # Import the MCP server module
        from linkedin_news_post.mcp_server import main as mcp_main
        
        # Run the MCP server
        mcp_main()
    except Exception as e:
        print(f"Error running MCP server: {e}")
        import traceback
        traceback.print_exc()

async def run_main_app():
    """Run the main application"""
    print("Starting main application...")
    
    try:
        # Import the main module
        import main
        
        # Run the main function
        if hasattr(main, 'run_graph'):
            await main.run_graph()
        elif hasattr(main, 'main'):
            await main.main()
        else:
            print("Could not find main function in main.py")
    except Exception as e:
        print(f"Error running main application: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        # Start the MCP server in a separate thread
        mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
        mcp_thread.start()
        
        # Wait for the MCP server to initialize
        print("Waiting for MCP server to initialize...")
        time.sleep(3)
        
        # Run the main application
        asyncio.run(run_main_app())
        
        # Keep the main thread alive
        while mcp_thread.is_alive():
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()