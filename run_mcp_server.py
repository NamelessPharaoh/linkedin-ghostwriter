#!/usr/bin/env python3
"""
Script to run the MCP server as a module.
"""

import os
import sys
import subprocess

def main():
    # Ensure the current directory is in the Python path
    current_dir = os.getcwd()
    
    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    env["PYTHONPATH"] = current_dir
    
    # Run the MCP server as a module
    subprocess.run(
        ["python", "-m", "linkedin_news_post.mcp_server"],
        env=env,
        cwd=current_dir,
    )

if __name__ == "__main__":
    main()