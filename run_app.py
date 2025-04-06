#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
import atexit
import threading

def stream_output(process, prefix):
    """Stream output from a process to stdout with a prefix"""
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[{prefix}] {line.strip()}")

    if process.poll() is not None:
        print(f"[{prefix}] Process exited with code {process.returncode}")

def cleanup(processes):
    """Clean up all running processes when the script exits"""
    print("Cleaning up processes...")
    for process in processes:
        if process.poll() is None:  # If process is still running
            try:
                print(f"Terminating process {process.pid}...")
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    print(f"Killing process {process.pid}...")
                    process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")

def main():
    # Ensure the current directory is in the Python path
    os.environ["PYTHONPATH"] = os.getcwd()

    processes = []
    threads = []

    try:
        # Start the MCP server
        print("Starting MCP server...")
        mcp_server = subprocess.Popen(
            ["python", "-m", "linkedin_news_post.mcp_server"],
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(mcp_server)
        print(f"MCP server started with PID {mcp_server.pid}")

        # Start a thread to stream MCP server output
        mcp_thread = threading.Thread(
            target=stream_output,
            args=(mcp_server, "MCP"),
            daemon=True
        )
        mcp_thread.start()
        threads.append(mcp_thread)

        # Register cleanup function to terminate processes on exit
        atexit.register(cleanup, processes)

        # Wait for the MCP server to initialize
        print("Waiting for MCP server to initialize...")
        time.sleep(3)

        # Check if MCP server is still running
        if mcp_server.poll() is not None:
            print(f"MCP server failed to start with exit code {mcp_server.returncode}")
            return 1

        # Start the main application
        print("Starting main application...")
        main_app = subprocess.Popen(
            ["python", "main.py"],
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(main_app)
        print(f"Main application started with PID {main_app.pid}")

        # Start a thread to stream main application output
        main_thread = threading.Thread(
            target=stream_output,
            args=(main_app, "MAIN"),
            daemon=True
        )
        main_thread.start()
        threads.append(main_thread)

        # Wait for processes to finish or user interrupt
        print("Both processes are running. Press Ctrl+C to stop.")
        while all(process.poll() is None for process in processes):
            time.sleep(0.1)

        # Check which process exited
        for process in processes:
            if process.poll() is not None:
                print(f"Process {process.pid} exited with code {process.returncode}")

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        cleanup(processes)
        # Wait for threads to finish
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1)

if __name__ == "__main__":
    sys.exit(main())