#!/usr/bin/env python3
"""
LinkedIn Ghostwriter Runner

This script runs the LinkedIn Ghostwriter application by:
1. Starting the modified MCP server in a separate process
2. Running the main application in the current process
3. Handling graceful shutdown of both components
"""

import os
import sys
import time
import signal
import subprocess
import atexit
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("linkedin-ghostwriter-runner")

def cleanup(process):
    """Clean up the MCP server process when the script exits"""
    if process and process.poll() is None:  # If process is still running
        try:
            logger.info("Terminating MCP server process...")
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                logger.info("Killing MCP server process...")
                process.kill()
        except Exception as e:
            logger.error(f"Error terminating process: {e}")

def run_mcp_server():
    """Start the MCP server in a separate process"""
    logger.info("Starting MCP server...")
    
    # Set up environment variables
    env = os.environ.copy()
    current_dir = os.getcwd()
    env["PYTHONPATH"] = current_dir
    
    # Run the modified MCP server script
    mcp_process = subprocess.Popen(
        ["python", "modified_mcp_server.py"],
        env=env,
        stdout=sys.stdout,  # Redirect stdout to the current process
        stderr=sys.stderr,  # Redirect stderr to the current process
    )
    
    # Register cleanup function to terminate the MCP server on exit
    atexit.register(cleanup, mcp_process)
    
    # Wait for the MCP server to initialize
    logger.info("Waiting for MCP server to initialize...")
    time.sleep(3)
    
    # Check if MCP server is still running
    if mcp_process.poll() is not None:
        logger.error(f"MCP server failed to start with exit code {mcp_process.returncode}")
        return None
    
    logger.info("MCP server started successfully")
    return mcp_process

def run_main_application():
    """Run the main LinkedIn Ghostwriter application"""
    logger.info("Running main application...")
    
    try:
        # Set up environment variables
        env = os.environ.copy()
        current_dir = os.getcwd()
        env["PYTHONPATH"] = current_dir
        
        # Import the main module
        sys.path.insert(0, current_dir)
        import main
        
        # Run the main application
        logger.info("Main application imported successfully")
        
        # The main module should have a run_graph function
        if hasattr(main, 'run_graph'):
            import asyncio
            asyncio.run(main.run_graph())
        else:
            logger.error("Main module does not have a run_graph function")
            return False
        
        logger.info("Main application completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error running main application: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False

def verify_linkedin_integration():
    """Verify the LinkedIn integration using the get_composio_integration.py script"""
    logger.info("Verifying LinkedIn integration...")
    
    try:
        # Run the get_composio_integration.py script
        result = subprocess.run(
            ["python", "get_composio_integration.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if the verification was successful
        if "Connected account verification completed successfully" in result.stdout:
            logger.info("LinkedIn integration verification completed successfully")
            return True
        else:
            logger.error("LinkedIn integration verification failed")
            logger.error(f"Output: {result.stdout}")
            return False
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error verifying LinkedIn integration: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Error: {e.stderr}")
        return False

def main():
    """Main entry point"""
    logger.info("Starting LinkedIn Ghostwriter application")
    
    # Verify LinkedIn integration
    if not verify_linkedin_integration():
        logger.error("LinkedIn integration verification failed. Exiting.")
        return 1
    
    # Start the MCP server
    mcp_process = run_mcp_server()
    if not mcp_process:
        logger.error("Failed to start MCP server. Exiting.")
        return 1
    
    try:
        # Run the main application
        success = run_main_application()
        if not success:
            logger.error("Main application failed. Exiting.")
            return 1
        
        # Keep the script running until the user interrupts it
        logger.info("Application is running. Press Ctrl+C to exit.")
        while mcp_process.poll() is None:
            time.sleep(0.1)
        
        # If we get here, the MCP server has exited
        logger.info("MCP server has exited.")
        return 0
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return 1
    finally:
        cleanup(mcp_process)

if __name__ == "__main__":
    sys.exit(main())